
from datetime import datetime, timezone

import httpx

from app.config import settings
from app.schemas import PlatformResult


async def post_to_telegram(message: str) -> PlatformResult:
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID

    if not token or not chat_id:
        return PlatformResult(
            platform="Telegram",
            status="failed",
            error="Telegram credentials are missing from .env"
        )

    api_url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message,
        "disable_web_page_preview": False
    }

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(api_url, json=payload)

        try:
            data = response.json()
        except ValueError:
            return PlatformResult(
                platform="Telegram",
                status="failed",
                error="Invalid response from Telegram API"
            )

        if response.status_code != 200 or not data.get("ok"):
            return PlatformResult(
                platform="Telegram",
                status="failed",
                error=data.get(
                    "description",
                    "Telegram API request failed"
                )
            )

        posted_message = data["result"]
        chat = posted_message["chat"]
        message_id = posted_message["message_id"]

        published_at = datetime.fromtimestamp(
            posted_message["date"],
            tz=timezone.utc
        )

        posted_url = None
        public_access = False

        if chat.get("username"):
            posted_url = (
                f"https://t.me/{chat['username']}/{message_id}"
            )
            public_access = True

        elif str(chat["id"]).startswith("-100"):
            channel_id = str(chat["id"])[4:]
            posted_url = f"https://t.me/c/{channel_id}/{message_id}"

        return PlatformResult(
            platform="Telegram",
            status="success",
            posted_url=posted_url,
            public_access=public_access,
            date=published_at.strftime("%Y-%m-%d"),
            time=published_at.strftime("%H:%M:%S"),
            error=None
        )

    except httpx.TimeoutException:
        return PlatformResult(
            platform="Telegram",
            status="failed",
            error="Telegram request timed out"
        )

    except httpx.RequestError:
        return PlatformResult(
            platform="Telegram",
            status="failed",
            error="Unable to connect to Telegram"
        )

    except (ValueError, KeyError, TypeError):
        return PlatformResult(
            platform="Telegram",
            status="failed",
            error="Unexpected response from Telegram"
        )
