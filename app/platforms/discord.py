
from datetime import datetime, timezone

import httpx

from app.config import settings
from app.schemas import PlatformResult


async def post_to_discord(message: str) -> PlatformResult:
    webhook_url = settings.DISCORD_WEBHOOK_URL

    if not webhook_url:
        return PlatformResult(
            platform="Discord",
            status="failed",
            error="Discord webhook URL is missing from .env"
        )

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                webhook_url,
                params={"wait": "true"},
                json={"content": message}
            )

        if response.status_code != 200:
            return PlatformResult(
                platform="Discord",
                status="failed",
                error=(
                    f"Discord returned HTTP {response.status_code}: "
                    f"{response.text[:300]}"
                )
            )

        posted_message = response.json()

        message_id = posted_message.get("id")
        channel_id = posted_message.get("channel_id")
        guild_id = posted_message.get("guild_id")
        timestamp = posted_message.get("timestamp")

        if not message_id or not channel_id or not timestamp:
            return PlatformResult(
                platform="Discord",
                status="failed",
                error="Discord published the request but returned incomplete message details"
            )

        published_at = datetime.fromisoformat(
            timestamp.replace("Z", "+00:00")
        )

        posted_url = None

        if guild_id:
            posted_url = (
                f"https://discord.com/channels/"
                f"{guild_id}/{channel_id}/{message_id}"
            )

        return PlatformResult(
            platform="Discord",
            status="success",
            posted_url=posted_url,
            public_access=False,
            date=published_at.strftime("%Y-%m-%d"),
            time=published_at.strftime("%H:%M:%S")
        )

    except httpx.TimeoutException:
        return PlatformResult(
            platform="Discord",
            status="failed",
            error="Discord request timed out"
        )

    except httpx.RequestError:
        return PlatformResult(
            platform="Discord",
            status="failed",
            error="Could not connect to Discord"
        )

    except (ValueError, KeyError, TypeError) as error:
        return PlatformResult(
            platform="Discord",
            status="failed",
            error=f"Could not process Discord response: {str(error)}"
        )
