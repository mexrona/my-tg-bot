import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    bot_token: str
    owner_id: int
    db_path: str


def load_settings() -> Settings:
    token = os.getenv("BOT_TOKEN", "").strip()
    owner_raw = os.getenv("OWNER_ID", "").strip()
    db_path = os.getenv("DB_PATH", "data/bot.db").strip()

    if not token:
        raise ValueError("BOT_TOKEN is not set in environment")
    if not owner_raw.isdigit():
        raise ValueError("OWNER_ID must be a numeric Telegram user id")

    return Settings(
        bot_token=token,
        owner_id=int(owner_raw),
        db_path=db_path,
    )
