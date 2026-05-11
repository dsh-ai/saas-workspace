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
