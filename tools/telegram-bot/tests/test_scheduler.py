from datetime import datetime, timezone
from pathlib import Path
import pytest
import pytest_asyncio

from src.scheduler import scan_drafts
from src.state import State, PostStatus


class _FakeCfg:
    """Minimal Config-like object — only attributes scan_drafts reads."""
    def __init__(self, drafts_dir: Path):
        self._drafts = drafts_dir

    @property
    def drafts_dir(self):
        return self._drafts


@pytest_asyncio.fixture
async def state(tmp_path):
    s = State(tmp_path / "test.db")
    await s.init()
    yield s
    await s.close()


def write_draft(drafts_dir: Path, post_id: str, publish_at: str = "2026-05-12T10:00:00+03:00") -> Path:
    f = drafts_dir / f"{post_id}.md"
    f.write_text(
        f"---\nid: {post_id}\npublish_at: {publish_at}\npillar: pain\nformat: text\n---\nBody"
    )
    return f


async def test_scan_drafts_registers_new(tmp_path, state):
    drafts = tmp_path / "drafts"
    drafts.mkdir()
    write_draft(drafts, "post-1")
    write_draft(drafts, "post-2")
    cfg = _FakeCfg(drafts)

    count = await scan_drafts(cfg, state)
    assert count == 2
    assert (await state.get("post-1"))["status"] == PostStatus.DRAFT
    assert (await state.get("post-2"))["status"] == PostStatus.DRAFT


async def test_scan_drafts_idempotent(tmp_path, state):
    drafts = tmp_path / "drafts"
    drafts.mkdir()
    write_draft(drafts, "post-1")
    cfg = _FakeCfg(drafts)
    await scan_drafts(cfg, state)
    await state.set_status("post-1", PostStatus.APPROVED)
    count = await scan_drafts(cfg, state)  # second scan — should NOT touch
    assert count == 0
    assert (await state.get("post-1"))["status"] == PostStatus.APPROVED


async def test_scan_drafts_skips_invalid(tmp_path, state, caplog):
    drafts = tmp_path / "drafts"
    drafts.mkdir()
    write_draft(drafts, "good")
    (drafts / "broken.md").write_text("---\nno_required_fields: true\n---\nbody")
    cfg = _FakeCfg(drafts)
    count = await scan_drafts(cfg, state)
    assert count == 1
    assert await state.get("good") is not None


async def test_scan_drafts_missing_dir_returns_zero(tmp_path, state):
    cfg = _FakeCfg(tmp_path / "nonexistent")
    assert await scan_drafts(cfg, state) == 0


from datetime import timedelta
from src.scheduler import trigger_publishes

UTC = timezone.utc


class _FakeMessage:
    def __init__(self, message_id): self.message_id = message_id


class _FakeBot:
    def __init__(self):
        self.calls = []
        self._counter = 1000

    async def send_message(self, chat_id, text, **kwargs):
        self.calls.append({"chat_id": chat_id, "text": text})
        self._counter += 1
        return _FakeMessage(self._counter)


class _FakeApp:
    def __init__(self):
        self.bot = _FakeBot()


class _FakeCfg2:
    def __init__(self, posts_root: Path):
        self.POSTS_ROOT = posts_root
        self.CHANNEL_ID = -1003253037787
        self.ADMIN_USER_ID = 31057348

    @property
    def drafts_dir(self): return self.POSTS_ROOT / "drafts"
    @property
    def published_dir(self): return self.POSTS_ROOT / "published"


async def test_trigger_publishes_moves_file_and_updates_state(tmp_path, state):
    posts_root = tmp_path / "posts"
    drafts = posts_root / "drafts"
    drafts.mkdir(parents=True)
    write_draft(drafts, "post-1", publish_at="2026-05-12T10:00:00+00:00")
    cfg = _FakeCfg2(posts_root)

    # Register + approve
    await state.register("post-1", datetime(2026, 5, 12, 10, tzinfo=UTC))
    await state.set_status("post-1", PostStatus.APPROVED)

    app = _FakeApp()
    now = datetime(2026, 5, 12, 10, 0, 1, tzinfo=UTC)
    sent = await trigger_publishes(app, cfg, state, now)

    assert sent == 1
    # Two sends: one to channel, one DM to admin
    assert len(app.bot.calls) == 2
    chat_ids = {c["chat_id"] for c in app.bot.calls}
    assert cfg.CHANNEL_ID in chat_ids
    assert cfg.ADMIN_USER_ID in chat_ids
    # File moved
    assert not (drafts / "post-1.md").exists()
    assert (posts_root / "published" / "post-1.md").exists()
    # State updated
    row = await state.get("post-1")
    assert row["status"] == PostStatus.PUBLISHED
    assert row["channel_message_id"] is not None


async def test_trigger_publishes_skips_unapproved(tmp_path, state):
    posts_root = tmp_path / "posts"
    drafts = posts_root / "drafts"
    drafts.mkdir(parents=True)
    write_draft(drafts, "post-1")
    cfg = _FakeCfg2(posts_root)
    await state.register("post-1", datetime(2026, 5, 12, 10, tzinfo=UTC))
    # still DRAFT
    app = _FakeApp()
    sent = await trigger_publishes(app, cfg, state, datetime(2026, 5, 12, 11, tzinfo=UTC))
    assert sent == 0
    assert (drafts / "post-1.md").exists()  # not moved
