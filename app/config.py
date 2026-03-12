from dataclasses import dataclass
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass(slots=True)
class Settings:
    bot_token: str
    channel_username: str
    bot_username: str
    db_path: str = "bot.db"


def load_settings() -> Settings:
    bot_token = os.getenv("BOT_TOKEN", "")
    channel_username = os.getenv("CHANNEL_USERNAME", "")
    bot_username = os.getenv("BOT_USERNAME", "")
    db_path = os.getenv("DB_PATH", "bot.db")

    if not bot_token:
        raise ValueError("BOT_TOKEN is not set")
    if not channel_username:
        raise ValueError("CHANNEL_USERNAME is not set")

    return Settings(
        bot_token=bot_token,
        channel_username=channel_username,
        bot_username=bot_username,
        db_path=db_path,
    )
