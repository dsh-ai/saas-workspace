from __future__ import annotations
import enum
from datetime import datetime, timedelta
from pathlib import Path
import aiosqlite


class PostStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"


SCHEMA = """
CREATE TABLE IF NOT EXISTS posts (
    id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    publish_at TEXT NOT NULL,
    approval_message_id INTEGER,
    channel_message_id INTEGER,
    last_alert_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

ALLOWED_UPDATE_FIELDS = {
    "approval_message_id",
    "channel_message_id",
    "last_alert_at",
    "publish_at",
}


class State:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self._conn: aiosqlite.Connection | None = None

    async def init(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = await aiosqlite.connect(self.db_path)
        self._conn.row_factory = aiosqlite.Row
        await self._conn.executescript(SCHEMA)
        await self._conn.commit()

    async def close(self) -> None:
        if self._conn:
            await self._conn.close()
            self._conn = None

    @property
    def conn(self) -> aiosqlite.Connection:
        if self._conn is None:
            raise RuntimeError("State.init() not called")
        return self._conn

    async def register(self, post_id: str, publish_at: datetime) -> None:
        await self.conn.execute(
            "INSERT OR IGNORE INTO posts (id, status, publish_at) VALUES (?, ?, ?)",
            (post_id, PostStatus.DRAFT.value, publish_at.isoformat()),
        )
        await self.conn.commit()

    async def get(self, post_id: str) -> dict | None:
        async with self.conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None

    async def set_status(self, post_id: str, status: PostStatus, **fields) -> None:
        sets = ["status = ?", "updated_at = datetime('now')"]
        params: list = [status.value]
        for k, v in fields.items():
            if k not in ALLOWED_UPDATE_FIELDS:
                raise ValueError(f"field not allowed for update: {k}")
            sets.append(f"{k} = ?")
            if isinstance(v, datetime):
                v = v.isoformat()
            params.append(v)
        params.append(post_id)
        await self.conn.execute(
            f"UPDATE posts SET {', '.join(sets)} WHERE id = ?", params
        )
        await self.conn.commit()

    async def list_due_for_approval(
        self, now: datetime, lead_hours: int = 24
    ) -> list[dict]:
        cutoff = (now + timedelta(hours=lead_hours)).isoformat()
        async with self.conn.execute(
            "SELECT * FROM posts WHERE status = ? AND publish_at <= ? ORDER BY publish_at",
            (PostStatus.DRAFT.value, cutoff),
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]

    async def list_due_for_publish(self, now: datetime) -> list[dict]:
        async with self.conn.execute(
            "SELECT * FROM posts WHERE status = ? AND publish_at <= ? ORDER BY publish_at",
            (PostStatus.APPROVED.value, now.isoformat()),
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]
