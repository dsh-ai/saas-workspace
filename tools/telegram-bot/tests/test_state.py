from datetime import datetime, timedelta, timezone
import pytest
import pytest_asyncio
from src.state import State, PostStatus

UTC = timezone.utc


@pytest_asyncio.fixture
async def state(tmp_path):
    s = State(tmp_path / "test.db")
    await s.init()
    yield s
    await s.close()


async def test_register_creates_draft(state):
    await state.register("p1", publish_at=datetime(2026, 5, 12, 10, tzinfo=UTC))
    row = await state.get("p1")
    assert row["status"] == PostStatus.DRAFT
    assert row["approval_message_id"] is None
    assert row["channel_message_id"] is None


async def test_register_is_idempotent(state):
    pub = datetime(2026, 5, 12, 10, tzinfo=UTC)
    await state.register("p1", publish_at=pub)
    await state.set_status("p1", PostStatus.APPROVED)
    await state.register("p1", publish_at=pub)  # should NOT reset
    row = await state.get("p1")
    assert row["status"] == PostStatus.APPROVED


async def test_get_returns_none_for_missing(state):
    assert await state.get("nope") is None


async def test_set_status_with_extra_fields(state):
    await state.register("p1", publish_at=datetime(2026, 5, 12, 10, tzinfo=UTC))
    await state.set_status("p1", PostStatus.PENDING_APPROVAL, approval_message_id=42)
    row = await state.get("p1")
    assert row["status"] == PostStatus.PENDING_APPROVAL
    assert row["approval_message_id"] == 42


async def test_list_due_for_approval_filters_by_window(state):
    now = datetime(2026, 5, 11, 10, tzinfo=UTC)
    await state.register("near", publish_at=datetime(2026, 5, 12, 9, tzinfo=UTC))   # in 23h
    await state.register("far",  publish_at=datetime(2026, 5, 15, 10, tzinfo=UTC))  # in 4d
    due = await state.list_due_for_approval(now=now, lead_hours=24)
    assert [p["id"] for p in due] == ["near"]


async def test_list_due_for_approval_excludes_non_draft(state):
    now = datetime(2026, 5, 11, 10, tzinfo=UTC)
    await state.register("p1", publish_at=datetime(2026, 5, 12, 9, tzinfo=UTC))
    await state.set_status("p1", PostStatus.APPROVED)
    due = await state.list_due_for_approval(now=now, lead_hours=24)
    assert due == []


async def test_list_due_for_publish(state):
    now = datetime(2026, 5, 12, 10, tzinfo=UTC)
    await state.register("ready", publish_at=datetime(2026, 5, 12, 9, tzinfo=UTC))
    await state.register("future", publish_at=datetime(2026, 5, 13, 9, tzinfo=UTC))
    await state.set_status("ready", PostStatus.APPROVED)
    await state.set_status("future", PostStatus.APPROVED)
    due = await state.list_due_for_publish(now=now)
    assert [p["id"] for p in due] == ["ready"]


async def test_list_due_for_publish_excludes_non_approved(state):
    now = datetime(2026, 5, 12, 10, tzinfo=UTC)
    await state.register("p1", publish_at=datetime(2026, 5, 12, 9, tzinfo=UTC))
    # still DRAFT
    due = await state.list_due_for_publish(now=now)
    assert due == []
