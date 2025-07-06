from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.backend.models.chat import Message
from app.backend.services.chat_service import generate_chat_response

router = APIRouter()

@router.post("/chat", tags=["chat"])
async def chat(request: Request, message: Message):
    return StreamingResponse(
        await generate_chat_response(request, message.content),
        media_type="application/json"
    )