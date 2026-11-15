
from fastapi.testclient import TestClient

from app.main import app

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


def test_accepts_valid_message():
    response = client.post(
        "/posting",
        json={
            "message": "Testing automated posting https://example.com"
        }
    )

    assert response.status_code == 200
