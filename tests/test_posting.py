
import asyncio

from fastapi.testclient import TestClient

from app.main import app
from app.schemas import PostingResponse, PlatformResult
from app.services import posting_service

client = TestClient(app)


def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "Automated Posting API is running"


def test_rejects_message_without_url():
    response = client.post(
        "/posting",
        json={"message": "Hello, this is a test message"}
    )

    assert response.status_code == 422


def test_rejects_message_with_multiple_urls():
    response = client.post(
        "/posting",
        json={
            "message": "Visit https://example.com and https://google.com"
        }
    )

    assert response.status_code == 422


def test_rejects_message_over_200_characters():
    response = client.post(
        "/posting",
        json={
            "message": "A" * 190 + " https://example.com"
        }
    )

    assert response.status_code == 422


def test_accepts_valid_message_without_live_publishing(monkeypatch):
    async def fake_publish_message(message):
        return PostingResponse(
            success=True,
            results=[
                PlatformResult(
                    platform="Telegram",
                    status="success"
                )
            ]
        )

    monkeypatch.setattr(
        "app.main.publish_message",
        fake_publish_message
    )

    response = client.post(
        "/posting",
        json={
            "message": "Testing automated posting https://example.com"
        }
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["results"][0]["platform"] == "Telegram"


def test_one_platform_failure_does_not_stop_others(monkeypatch):
    async def successful_post(message):
        return PlatformResult(
            platform="Test Platform",
            status="success"
        )

    async def failed_post(message):
        raise RuntimeError("Platform is unavailable")

    monkeypatch.setattr(posting_service, "post_to_telegram", failed_post)
    monkeypatch.setattr(posting_service, "post_to_discord", successful_post)
    monkeypatch.setattr(posting_service, "post_to_bluesky", successful_post)
    monkeypatch.setattr(posting_service, "post_to_slack", successful_post)
    monkeypatch.setattr(posting_service, "post_to_google_chat", successful_post)

    result = asyncio.run(
        posting_service.publish_message(
            "Test message https://example.com"
        )
    )

    assert len(result.results) == 5
    assert result.results[0].status == "failed"
    assert all(
        item.status == "success"
        for item in result.results[1:]
    )
    assert result.success is True


def test_overall_failure_when_all_platforms_fail(monkeypatch):
    async def failed_post(message):
        raise RuntimeError("Platform is unavailable")

    monkeypatch.setattr(posting_service, "post_to_telegram", failed_post)
    monkeypatch.setattr(posting_service, "post_to_discord", failed_post)
    monkeypatch.setattr(posting_service, "post_to_bluesky", failed_post)
    monkeypatch.setattr(posting_service, "post_to_slack", failed_post)
    monkeypatch.setattr(posting_service, "post_to_google_chat", failed_post)

    result = asyncio.run(
        posting_service.publish_message(
            "Test message https://example.com"
        )
    )

    assert len(result.results) == 5
    assert all(
        item.status == "failed"
        for item in result.results
    )
    assert result.success is False


def test_accepts_www_link_without_live_publishing(monkeypatch):
    async def fake_publish_message(message):
        return PostingResponse(
            success=True,
            results=[
                PlatformResult(
                    platform="Telegram",
                    status="success"
                )
            ]
        )

    monkeypatch.setattr(
        "app.main.publish_message",
        fake_publish_message
    )

    response = client.post(
        "/posting",
        json={
            "message": "Visit our website www.example.com"
        }
    )

    assert response.status_code == 200
    assert response.json()["success"] is True


def test_invalid_platform_response_does_not_crash(monkeypatch):
    async def invalid_post(message):
        return None

    async def successful_post(message):
        return PlatformResult(
            platform="Test Platform",
            status="success"
        )

    monkeypatch.setattr(posting_service, "post_to_telegram", invalid_post)
    monkeypatch.setattr(posting_service, "post_to_discord", successful_post)
    monkeypatch.setattr(posting_service, "post_to_bluesky", successful_post)
    monkeypatch.setattr(posting_service, "post_to_slack", successful_post)
    monkeypatch.setattr(posting_service, "post_to_google_chat", successful_post)

    result = asyncio.run(
        posting_service.publish_message(
            "Test message https://example.com"
        )
    )

    assert len(result.results) == 5
    assert result.results[0].status == "failed"
    assert result.results[0].error == "Invalid response from platform integration"
    assert all(item.status == "success" for item in result.results[1:])
    assert result.success is True
