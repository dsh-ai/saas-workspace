from __future__ import annotations
import logging
from functools import wraps
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from src.config import Config

log = logging.getLogger(__name__)
cfg = Config()


def admin_only(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user is None or user.id != cfg.ADMIN_USER_ID:
            if update.message:
                await update.message.reply_text("Не авторизован.")
            log.warning("unauthorized access attempt: user=%s", user)
            return
        return await func(update, context)
    return wrapper


@admin_only
async def cmd_start(update: Update, _ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Unilist bot готов.\nКоманды:\n/pending — посты, ждущие approve"
    )


@admin_only
async def cmd_pending(update: Update, _ctx: ContextTypes.DEFAULT_TYPE):
    # Placeholder. Real implementation in Task 5.
    await update.message.reply_text("(пока пусто)")


def build_app() -> Application:
    app = Application.builder().token(cfg.BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("pending", cmd_pending))
    return app
