from __future__ import annotations
import asyncio
import logging
import sys

from src.bot import build_app
from src.config import Config
from src.scheduler import run_scheduler
from src.state import State

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("unilist-bot")


async def cmd_run() -> None:
    cfg = Config()
    state = State(cfg.STATE_DB)
    await state.init()
    app = build_app()
    app.bot_data["state"] = state

    log.info("starting bot polling + scheduler")
    async with app:
        await app.start()
        await app.updater.start_polling()
        scheduler_task = asyncio.create_task(run_scheduler(app, cfg, state))
        try:
            await scheduler_task
        finally:
            await app.updater.stop()
            await app.stop()
            await state.close()


async def cmd_list() -> None:
    cfg = Config()
    state = State(cfg.STATE_DB)
    await state.init()
    try:
        async with state.conn.execute(
            "SELECT id, status, publish_at, approval_message_id, channel_message_id "
            "FROM posts ORDER BY publish_at"
        ) as cur:
            rows = await cur.fetchall()
        if not rows:
            print("(no posts)")
            return
        print(f"{'publish_at':30} {'status':20} {'id':40} approval channel")
        for r in rows:
            print(
                f"{r['publish_at']:30} {r['status']:20} {r['id']:40} "
                f"{r['approval_message_id'] or '-'} {r['channel_message_id'] or '-'}"
            )
    finally:
        await state.close()


COMMANDS = {"run": cmd_run, "list": cmd_list}


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd not in COMMANDS:
        print(f"unknown command: {cmd}. valid: {', '.join(COMMANDS)}", file=sys.stderr)
        sys.exit(2)
    try:
        asyncio.run(COMMANDS[cmd]())
    except KeyboardInterrupt:
        log.info("interrupted")


if __name__ == "__main__":
    main()
