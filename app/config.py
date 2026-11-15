import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)


class Settings:
    BLUESKY_HANDLE = os.getenv("BLUESKY_HANDLE")
    BLUESKY_APP_PASSWORD = os.getenv("BLUESKY_APP_PASSWORD")

    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

    SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


    GOOGLE_CHAT_WEBHOOK_URL = os.getenv("GOOGLE_CHAT_WEBHOOK_URL")

settings = Settings()