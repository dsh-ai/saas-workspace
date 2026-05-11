from __future__ import annotations
import logging
import shutil
from pathlib import Path
from telegram.ext import Application

from src.config import Config
from src.post import Post
from src.state import State, PostStatus

log = logging.getLogger(__name__)


async def publish_post(app: Application, cfg: Config, state: State, post: Post) -> int:
    """Send post body to channel, move file to published/, update DB. Returns channel_message_id."""
    msg = await app.bot.send_message(
        chat_id=cfg.CHANNEL_ID,
        text=post.body,
        parse_mode="Markdown",
    )
    cfg.published_dir.mkdir(parents=True, exist_ok=True)
    new_path = cfg.published_dir / post.path.name
    shutil.move(str(post.path), str(new_path))
    await state.set_status(
        post.id, PostStatus.PUBLISHED, channel_message_id=msg.message_id
    )
    try:
        await app.bot.send_message(
            chat_id=cfg.ADMIN_USER_ID,
            text=f"📤 Опубликован: `{post.id}` → message_id {msg.message_id}",
            parse_mode="Markdown",
        )
    except Exception:
        log.exception("admin confirmation DM failed for %s", post.id)
    log.info("published %s → channel msg %s", post.id, msg.message_id)
    return msg.message_id
