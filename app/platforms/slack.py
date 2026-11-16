
from datetime import datetime, timezone

import httpx

from app.config import settings
from app.schemas import PlatformResult


async def post_to_slack(message: str) -> PlatformResult:
    webhook_url = settings.SLACK_WEBHOOK_URL

    if not webhook_url:
        return PlatformResult(
            platform="Slack",
            status="failed",
            error="Slack webhook URL is missing from .env"
        )

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                webhook_url,
                json={"text": message}
            )

        if response.status_code != 200:
            return PlatformResult(
                platform="Slack",
                status="failed",
                error=f"Slack returned HTTP {response.status_code}"
            )

        if response.text.strip() != "ok":
            return PlatformResult(
                platform="Slack",
                status="failed",
                error="Slack rejected the message"
            )

        published_at = datetime.now(timezone.utc)

        return PlatformResult(
            platform="Slack",
            status="success",
            posted_url=None,
            public_access=False,
            date=published_at.strftime("%Y-%m-%d"),
            time=published_at.strftime("%H:%M:%S"),
            error=None
        )

    except httpx.TimeoutException:
        return PlatformResult(
            platform="Slack",
            status="failed",
            error="Slack request timed out"
        )

    except httpx.RequestError:
        return PlatformResult(
            platform="Slack",
            status="failed",
            error="Could not connect to Slack"
        )
