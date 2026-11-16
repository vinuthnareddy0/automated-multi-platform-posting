
from datetime import datetime, timezone
import re

import httpx

from app.config import settings
from app.schemas import PlatformResult


URL_PATTERN = re.compile(
    r"""https?://[^\s<>"']+|www\.[^\s<>"']+""",
    re.IGNORECASE
)


async def post_to_bluesky(message: str) -> PlatformResult:
    handle = settings.BLUESKY_HANDLE
    app_password = settings.BLUESKY_APP_PASSWORD

    if not handle or not app_password:
        return PlatformResult(
            platform="Bluesky",
            status="failed",
            error="Bluesky credentials are missing from .env"
        )

    base_url = "https://bsky.social/xrpc"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            login_response = await client.post(
                f"{base_url}/com.atproto.server.createSession",
                json={
                    "identifier": handle,
                    "password": app_password
                }
            )

            if login_response.status_code != 200:
                return PlatformResult(
                    platform="Bluesky",
                    status="failed",
                    error="Bluesky authentication failed. Check your credentials."
                )

            session = login_response.json()
            access_token = session["accessJwt"]
            did = session["did"]

            facets = []
            url_match = URL_PATTERN.search(message)

            if url_match:
                matched_url = url_match.group().rstrip(".,!?;:)]}")

                start = message.find(matched_url)
                byte_start = len(
                    message[:start].encode("utf-8")
                )
                byte_end = byte_start + len(
                    matched_url.encode("utf-8")
                )

                link = matched_url

                if link.lower().startswith("www."):
                    link = "https://" + link

                facets.append({
                    "index": {
                        "byteStart": byte_start,
                        "byteEnd": byte_end
                    },
                    "features": [{
                        "$type": "app.bsky.richtext.facet#link",
                        "uri": link
                    }]
                })

            published_at = datetime.now(timezone.utc)

            record = {
                "$type": "app.bsky.feed.post",
                "text": message,
                "createdAt": published_at.isoformat()
            }

            if facets:
                record["facets"] = facets

            post_response = await client.post(
                f"{base_url}/com.atproto.repo.createRecord",
                headers={
                    "Authorization": f"Bearer {access_token}"
                },
                json={
                    "repo": did,
                    "collection": "app.bsky.feed.post",
                    "record": record
                }
            )

            if post_response.status_code != 200:
                return PlatformResult(
                    platform="Bluesky",
                    status="failed",
                    error=(
                        f"Bluesky publishing failed: "
                        f"HTTP {post_response.status_code}"
                    )
                )

            post_data = post_response.json()
            post_uri = post_data["uri"]
            post_id = post_uri.rsplit("/", 1)[-1]

            profile_handle = handle.lstrip("@")

            posted_url = (
                f"https://bsky.app/profile/"
                f"{profile_handle}/post/{post_id}"
            )

            return PlatformResult(
                platform="Bluesky",
                status="success",
                posted_url=posted_url,
                public_access=True,
                date=published_at.strftime("%Y-%m-%d"),
                time=published_at.strftime("%H:%M:%S"),
                error=None
            )

    except httpx.TimeoutException:
        return PlatformResult(
            platform="Bluesky",
            status="failed",
            error="Bluesky request timed out"
        )

    except httpx.RequestError:
        return PlatformResult(
            platform="Bluesky",
            status="failed",
            error="Could not connect to Bluesky"
        )

    except (ValueError, KeyError, TypeError):
        return PlatformResult(
            platform="Bluesky",
            status="failed",
            error="Unexpected response from Bluesky"
        )
