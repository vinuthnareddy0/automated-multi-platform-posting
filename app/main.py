
from fastapi import FastAPI

from app.schemas import PostingRequest, PostingResponse
from app.services.posting_service import publish_message

app = FastAPI(
    title="Automated Multi-Platform Posting API",
    description="Publish a message across supported platforms.",
    version="1.0.0"
)


@app.get("/")
async def home():
    return {
        "message": "Automated Posting API is running",
        "docs": "/docs"
    }


@app.post("/posting", response_model=PostingResponse)
async def create_post(request: PostingRequest):
    return await publish_message(request.message)
