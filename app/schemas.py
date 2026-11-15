import re

from pydantic import BaseModel, Field, field_validator, HttpUrl, TypeAdapter


url_adapter = TypeAdapter(HttpUrl)

URL_PATTERN = re.compile(r"""(?i)\b(?:https?://|www\.)[^\s<>"']+""")


class PostingRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=200,
        description="Message to publish, including exactly one CTA URL"
    )

    @field_validator("message")
    @classmethod
    def validate_message(cls, message):
        if not message.strip():
            raise ValueError("Message cannot be empty")

        urls = URL_PATTERN.findall(message)

        if len(urls) != 1:
            raise ValueError("Message must contain exactly one CTA link")

        url = urls[0].rstrip(".,!?;:)]}")

        if url.lower().startswith("www."):
            url = "https://" + url

        try:
            url_adapter.validate_python(url)
        except Exception:
            raise ValueError("The CTA link must be a valid HTTP or HTTPS URL")

        return message


class PlatformResult(BaseModel):
    platform: str
    status: str
    posted_url: str | None = None
    public_access: bool = False
    date: str | None = None
    time: str | None = None
    error: str | None = None


class PostingResponse(BaseModel):
    success: bool
    results: list[PlatformResult]