from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.models.chat_schema import Message
from app.chatbot import bot
from app.services.chat_service import generate_chat_response

router = APIRouter()

@router.post("/chat", tags=["chat"])
async def chat(message: Message):
    return StreamingResponse(
        await generate_chat_response(message.content),
        media_type="application/json"
    )