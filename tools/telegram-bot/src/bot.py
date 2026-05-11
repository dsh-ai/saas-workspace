from __future__ import annotations
import logging
from datetime import datetime, timedelta
from functools import wraps
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes,
)

from src.config import Config
from src.post import Post
from src.state import State, PostStatus

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


def approval_keyboard(post_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Approve", callback_data=f"approve:{post_id}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"reject:{post_id}"),
        InlineKeyboardButton("⏰ Snooze 24h", callback_data=f"snooze:{post_id}"),
    ]])


def format_approval_card(post: Post) -> str:
    return (
        f"📝 *Пост на approve*\n"
        f"`{post.id}` → {post.publish_at:%Y-%m-%d %H:%M %Z}\n"
        f"pillar: {post.pillar} · format: {post.format}\n\n"
        f"{post.body}"
    )


async def send_for_approval(app: Application, state: State, post: Post) -> int:
    """Send approval card to admin, mark post as pending_approval, return message_id."""
    msg = await app.bot.send_message(
        chat_id=cfg.ADMIN_USER_ID,
        text=format_approval_card(post),
        parse_mode="Markdown",
        reply_markup=approval_keyboard(post.id),
    )
    await state.set_status(
        post.id,
        PostStatus.PENDING_APPROVAL,
        approval_message_id=msg.message_id,
    )
    return msg.message_id


async def on_button(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query is None:
        return
    await query.answer()
    if query.from_user.id != cfg.ADMIN_USER_ID:
        return

    try:
        action, post_id = query.data.split(":", 1)
    except ValueError:
        log.warning("malformed callback_data: %s", query.data)
        return

    state: State = ctx.application.bot_data.get("state")
    if state is None:
        log.error("state not in bot_data — bootstrapping issue")
        return

    row = await state.get(post_id)
    if row is None:
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(f"⚠️ Пост `{post_id}` не найден в БД.", parse_mode="Markdown")
        return

    if action == "approve":
        await state.set_status(post_id, PostStatus.APPROVED)
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(f"✅ Approved: `{post_id}`", parse_mode="Markdown")
    elif action == "reject":
        await state.set_status(post_id, PostStatus.REJECTED)
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(f"❌ Rejected: `{post_id}`", parse_mode="Markdown")
    elif action == "snooze":
        new_at = (datetime.fromisoformat(row["publish_at"]) + timedelta(hours=24)).isoformat()
        await state.set_status(post_id, PostStatus.DRAFT, publish_at=new_at)
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(
            f"⏰ Snoozed +24h: `{post_id}` → {new_at}", parse_mode="Markdown"
        )
    else:
        log.warning("unknown action: %s", action)


@admin_only
async def on_voice(update: Update, _ctx: ContextTypes.DEFAULT_TYPE):
    """Save incoming voice message as OGG in raw-inbox/."""
    voice = update.message.voice
    if voice is None:
        return
    cfg.RAW_INBOX.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(pytz.timezone(cfg.TZ)).strftime("%Y-%m-%d-%H%M%S")
    filename = f"{ts}-voice.ogg"
    target = cfg.RAW_INBOX / filename
    tg_file = await voice.get_file()
    await tg_file.download_to_drive(target)
    log.info("saved voice: %s (%ss)", filename, voice.duration)
    await update.message.reply_text(
        f"🎙 Голосовое записано: `{filename}` ({voice.duration}с)\n"
        f"Расшифруй (в TG встроено) и пришли текст следующим сообщением — "
        f"бот запишет к этой записи.",
        parse_mode="Markdown",
    )


@admin_only
async def on_text(update: Update, _ctx: ContextTypes.DEFAULT_TYPE):
    """Save any non-command text from admin as a markdown note in raw-inbox/."""
    msg = update.message
    if msg is None or not msg.text or msg.text.startswith("/"):
        return
    cfg.RAW_INBOX.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(pytz.timezone(cfg.TZ)).strftime("%Y-%m-%d-%H%M%S")
    filename = f"{ts}-note.md"
    target = cfg.RAW_INBOX / filename
    target.write_text(f"# {ts}\n\n{msg.text}\n", encoding="utf-8")
    log.info("saved note: %s (%d chars)", filename, len(msg.text))
    await msg.reply_text(
        f"📝 Заметка записана: `{filename}` ({len(msg.text)} символов)",
        parse_mode="Markdown",
    )


def build_app() -> Application:
    app = Application.builder().token(cfg.BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("pending", cmd_pending))
    app.add_handler(CallbackQueryHandler(on_button))
    app.add_handler(MessageHandler(filters.VOICE, on_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    return app
