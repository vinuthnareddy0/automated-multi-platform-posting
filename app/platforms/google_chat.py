
from datetime import datetime, timezone

import httpx

from app.config import settings
from app.schemas import PlatformResult


async def post_to_google_chat(message: str) -> PlatformResult:
    webhook_url = settings.GOOGLE_CHAT_WEBHOOK_URL

    if not webhook_url:
        return PlatformResult(
            platform="Google Chat",
            status="failed",
            error="Google Chat webhook URL is missing from .env"
        )

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                webhook_url,
                json={"text": message}
            )

        if response.status_code not in (200, 201):
            return PlatformResult(
                platform="Google Chat",
                status="failed",
                error=f"Google Chat returned HTTP {response.status_code}"
            )

        published_at = datetime.now(timezone.utc)

        return PlatformResult(
            platform="Google Chat",
            status="success",
            posted_url=None,
            public_access=False,
            date=published_at.strftime("%Y-%m-%d"),
            time=published_at.strftime("%H:%M:%S"),
            error=None
        )

    except httpx.TimeoutException:
        return PlatformResult(
            platform="Google Chat",
            status="failed",
            error="Google Chat request timed out"
        )

    except httpx.RequestError:
        return PlatformResult(
            platform="Google Chat",
            status="failed",
            error="Could not connect to Google Chat"
        )
