from app.config import settings

from app.platforms import telegram, discord, bluesky, slack, google_chat

class FakeResponse:
    def __init__(self, status_code, data=None, text =""):
        self.status_code = status_code
        self.data = data
        self.text = text

    def json(self):
        return self.data


class FakeClient:
    def __init__(self, response):
        self.responses = response if isinstance(response, list) else [response]

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def post(self, *args, **kwargs):
        return self.responses.pop(0)


def test_telegram_success(monkeypatch):
    monkeypatch.setattr(settings, "TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setattr(settings, "TELEGRAM_CHAT_ID", "-1001234567890")

    response = FakeResponse(
        200,
        {
            "ok": True,
            "result": {
                "message_id": 10,
                "date": 1794800000,
                "chat": {
                    "id": -1001234567890
                }
            }
        }
    )

    monkeypatch.setattr(
        telegram.httpx,
        "AsyncClient",
        lambda **kwargs: FakeClient(response)
    )

    import asyncio

    result = asyncio.run(
        telegram.post_to_telegram("Test message https://example.com")
    )

    assert result.status == "success"
    assert result.platform == "Telegram"
    assert result.posted_url is not None
    assert result.public_access is False


def test_telegram_api_failure(monkeypatch):
    monkeypatch.setattr(settings, "TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setattr(settings, "TELEGRAM_CHAT_ID", "-1001234567890")

    response = FakeResponse(
        400,
        {
            "ok": False,
            "description": "Bad Request"
        }
    )

    monkeypatch.setattr(
        telegram.httpx,
        "AsyncClient",
        lambda **kwargs: FakeClient(response)
    )

    import asyncio

    result = asyncio.run(
        telegram.post_to_telegram("Test message https://example.com")
    )

    assert result.status == "failed"
    assert result.platform == "Telegram"
    assert result.error == "Bad Request"


def test_telegram_missing_credentials(monkeypatch):
    monkeypatch.setattr(settings, "TELEGRAM_BOT_TOKEN", "")
    monkeypatch.setattr(settings, "TELEGRAM_CHAT_ID", "")

    import asyncio

    result = asyncio.run(
        telegram.post_to_telegram("Test message https://example.com")
    )

    assert result.status == "failed"
    assert result.error == "Telegram credentials are missing from .env"


def test_discord_success(monkeypatch):
    monkeypatch.setattr(
        settings,
        "DISCORD_WEBHOOK_URL",
        "https://discord.com/api/webhooks/test"
    )

    response = FakeResponse(
        200,
        {
            "id": "123456789",
            "channel_id": "987654321",
            "guild_id": "111222333",
            "timestamp": "2026-11-16T04:00:00+00:00"
        }
    )

    monkeypatch.setattr(
        discord.httpx,
        "AsyncClient",
        lambda **kwargs: FakeClient(response)
    )

    import asyncio

    result = asyncio.run(
        discord.post_to_discord(
            "Test message https://example.com"
        )
    )

    assert result.status == "success"
    assert result.platform == "Discord"
    assert result.posted_url is not None
    assert result.public_access is False

def test_discord_api_failure(monkeypatch):
    monkeypatch.setattr(
        settings,
        "DISCORD_WEBHOOK_URL",
        "https://discord.com/api/webhooks/test"
    )

    response = FakeResponse(400, {})

    monkeypatch.setattr(
        discord.httpx,
        "AsyncClient",
        lambda **kwargs: FakeClient(response)
    )

    import asyncio

    result = asyncio.run(
        discord.post_to_discord(
            "Test message https://example.com"
        )
    )

    assert result.status == "failed"
    assert result.platform == "Discord"
    assert "HTTP 400" in result.error

def test_bluesky_success(monkeypatch):
    import asyncio

    monkeypatch.setattr(settings, "BLUESKY_HANDLE", "test.bsky.social")
    monkeypatch.setattr(settings, "BLUESKY_APP_PASSWORD", "test-password")

    responses = [
        FakeResponse(200, {
            "accessJwt": "test-access-token",
            "did": "did:plc:test"
        }),
        FakeResponse(200, {
            "uri": "at://did:plc:test/app.bsky.feed.post/abc123"
        })
    ]

    monkeypatch.setattr(
        bluesky.httpx,
        "AsyncClient",
        lambda **kwargs: FakeClient(responses)
    )

    result = asyncio.run(
        bluesky.post_to_bluesky("Test message https://example.com")
    )

    assert result.status == "success"
    assert result.platform == "Bluesky"
    assert result.posted_url == (
        "https://bsky.app/profile/test.bsky.social/post/abc123"
    )
    assert result.public_access is True


def test_bluesky_publishing_failure(monkeypatch):
    import asyncio

    monkeypatch.setattr(settings, "BLUESKY_HANDLE", "test.bsky.social")
    monkeypatch.setattr(settings, "BLUESKY_APP_PASSWORD", "test-password")

    responses = [
        FakeResponse(200, {
            "accessJwt": "test-access-token",
            "did": "did:plc:test"
        }),
        FakeResponse(500, {})
    ]

    monkeypatch.setattr(
        bluesky.httpx,
        "AsyncClient",
        lambda **kwargs: FakeClient(responses)
    )

    result = asyncio.run(
        bluesky.post_to_bluesky("Test message https://example.com")
    )

    assert result.status == "failed"
    assert result.platform == "Bluesky"
    assert "HTTP 500" in result.error

def test_slack_success(monkeypatch):
    import asyncio

    monkeypatch.setattr(
        settings, "SLACK_WEBHOOK_URL", "https://example.com/slack"
    )

    response = FakeResponse(200, text="ok")

    monkeypatch.setattr(
        slack.httpx,
        "AsyncClient",
        lambda **kwargs: FakeClient(response)
    )

    result = asyncio.run(
        slack.post_to_slack("Test message https://example.com")
    )

    assert result.status == "success"
    assert result.platform == "Slack"
    assert result.posted_url is None


def test_slack_api_failure(monkeypatch):
    import asyncio

    monkeypatch.setattr(
        settings, "SLACK_WEBHOOK_URL", "https://example.com/slack"
    )

    response = FakeResponse(500, text="error")

    monkeypatch.setattr(
        slack.httpx,
        "AsyncClient",
        lambda **kwargs: FakeClient(response)
    )

    result = asyncio.run(
        slack.post_to_slack("Test message https://example.com")
    )

    assert result.status == "failed"
    assert "HTTP 500" in result.error


def test_google_chat_success(monkeypatch):
    import asyncio

    monkeypatch.setattr(
        settings,
        "GOOGLE_CHAT_WEBHOOK_URL",
        "https://example.com/google-chat"
    )

    response = FakeResponse(200)

    monkeypatch.setattr(
        google_chat.httpx,
        "AsyncClient",
        lambda **kwargs: FakeClient(response)
    )

    result = asyncio.run(
        google_chat.post_to_google_chat(
            "Test message https://example.com"
        )
    )

    assert result.status == "success"
    assert result.platform == "Google Chat"
    assert result.posted_url is None


def test_google_chat_api_failure(monkeypatch):
    import asyncio

    monkeypatch.setattr(
        settings,
        "GOOGLE_CHAT_WEBHOOK_URL",
        "https://example.com/google-chat"
    )

    response = FakeResponse(500)

    monkeypatch.setattr(
        google_chat.httpx,
        "AsyncClient",
        lambda **kwargs: FakeClient(response)
    )

    result = asyncio.run(
        google_chat.post_to_google_chat(
            "Test message https://example.com"
        )
    )

    assert result.status == "failed"
    assert "HTTP 500" in result.error