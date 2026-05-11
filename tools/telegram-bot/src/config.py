import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the saas-workspace .secrets/ if present, else local .env
SECRETS_ENV = Path(__file__).resolve().parents[3] / ".secrets" / "telegram-bot.env"
if SECRETS_ENV.exists():
    load_dotenv(SECRETS_ENV)
else:
    load_dotenv()


class Config:
    BOT_TOKEN: str = os.environ["TELEGRAM_BOT_TOKEN"]
    ADMIN_USER_ID: int = int(os.environ["TELEGRAM_ADMIN_USER_ID"])
    CHANNEL_ID: int = int(os.environ["TELEGRAM_CHANNEL_ID"])
    POSTS_ROOT: Path = Path(os.environ["POSTS_ROOT"])
    STATE_DB: Path = Path(os.environ["STATE_DB"])
    TZ: str = os.environ.get("TZ", "Europe/Moscow")

    @property
    def drafts_dir(self) -> Path:
        return self.POSTS_ROOT / "drafts"

    @property
    def scheduled_dir(self) -> Path:
        return self.POSTS_ROOT / "scheduled"

    @property
    def published_dir(self) -> Path:
        return self.POSTS_ROOT / "published"
