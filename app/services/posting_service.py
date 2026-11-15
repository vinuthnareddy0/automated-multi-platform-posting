
import asyncio

from app.platforms.telegram import post_to_telegram
from app.platforms.discord import post_to_discord
from app.platforms.bluesky import post_to_bluesky
from app.platforms.slack import post_to_slack
from app.platforms.google_chat import post_to_google_chat
from app.schemas import PostingResponse, PlatformResult


async def publish_message(message: str) -> PostingResponse:
    platform_functions = [
        ("Telegram", post_to_telegram),
        ("Discord", post_to_discord),
        ("Bluesky", post_to_bluesky),
        ("Slack", post_to_slack),
        ("Google Chat", post_to_google_chat)
    ]

    results = await asyncio.gather(
        *(function(message) for _, function in platform_functions),
        return_exceptions=True
    )

    platform_results = []

    for (platform, _), result in zip(platform_functions, results):
        if isinstance(result, Exception):
            platform_results.append(
                PlatformResult(
                    platform=platform,
                    status="failed",
                    error="Unexpected error while publishing"
                )
            )
        else:
            platform_results.append(result)

    return PostingResponse(
        success=any(
            result.status == "success"
            for result in platform_results
        ),
        results=platform_results
    )
