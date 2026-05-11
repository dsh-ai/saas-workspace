from __future__ import annotations
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
import pytz
from telegram.ext import Application

from src.config import Config
from src.post import Post
from src.state import State, PostStatus
from src.bot import send_for_approval

log = logging.getLogger(__name__)

POLL_SEC = 60
APPROVAL_LEAD_HOURS = 24
ESCALATION_LEAD_HOURS = 2
ESCALATION_THROTTLE_MIN = 60


async def scan_drafts(cfg: Config, state: State) -> int:
    """Find new .md files in drafts/, register them in DB. Returns count registered."""
    if not cfg.drafts_dir.exists():
        return 0
    count = 0
    for path in sorted(cfg.drafts_dir.glob("*.md")):
        try:
            post = Post.from_file(path)
        except Exception as e:
            log.warning("skip %s: %s", path, e)
            continue
        existing = await state.get(post.id)
        if existing is None:
            await state.register(post.id, post.publish_at)
            log.info("registered draft: %s (publish_at=%s)", post.id, post.publish_at)
            count += 1
    return count


async def trigger_approvals(app: Application, cfg: Config, state: State, now: datetime) -> int:
    """Send approval cards for posts due within APPROVAL_LEAD_HOURS. Returns count sent."""
    due = await state.list_due_for_approval(now=now, lead_hours=APPROVAL_LEAD_HOURS)
    sent = 0
    for row in due:
        path = cfg.drafts_dir / f"{row['id']}.md"
        if not path.exists():
            log.error("draft file missing for registered post: %s", row["id"])
            continue
        try:
            post = Post.from_file(path)
            await send_for_approval(app, state, post)
            sent += 1
        except Exception:
            log.exception("failed to send approval for %s", row["id"])
    return sent


async def trigger_escalations(app: Application, cfg: Config, state: State, now: datetime) -> int:
    """Alert admin about pending posts close to publish_at. Throttled per post."""
    threshold = (now + timedelta(hours=ESCALATION_LEAD_HOURS)).isoformat()
    throttle_cutoff = (now - timedelta(minutes=ESCALATION_THROTTLE_MIN)).isoformat()
    async with state.conn.execute(
        """SELECT * FROM posts
           WHERE status = ?
             AND publish_at <= ?
             AND (last_alert_at IS NULL OR last_alert_at < ?)
           ORDER BY publish_at""",
        (PostStatus.PENDING_APPROVAL.value, threshold, throttle_cutoff),
    ) as cur:
        rows = await cur.fetchall()

    sent = 0
    for row in rows:
        try:
            await app.bot.send_message(
                chat_id=cfg.ADMIN_USER_ID,
                text=(
                    f"🚨 *ЭСКАЛАЦИЯ*\n"
                    f"Пост `{row['id']}` выходит в {row['publish_at']}, "
                    f"но всё ещё не одобрен."
                ),
                parse_mode="Markdown",
            )
            await state.set_status(
                row["id"],
                PostStatus.PENDING_APPROVAL,  # status unchanged
                last_alert_at=now.isoformat(),
            )
            sent += 1
        except Exception:
            log.exception("escalation send failed for %s", row["id"])
    return sent


async def trigger_publishes(app: Application, cfg: Config, state: State, now: datetime) -> int:
    """Stub — real implementation in Task 7."""
    return 0


async def run_scheduler(app: Application, cfg: Config, state: State) -> None:
    tz = pytz.timezone(cfg.TZ)
    log.info("scheduler started, poll=%ss, tz=%s", POLL_SEC, cfg.TZ)
    while True:
        now = datetime.now(tz)
        try:
            await scan_drafts(cfg, state)
            await trigger_approvals(app, cfg, state, now)
            await trigger_escalations(app, cfg, state, now)
            await trigger_publishes(app, cfg, state, now)
        except Exception:
            log.exception("scheduler tick failed")
        await asyncio.sleep(POLL_SEC)
