from fastapi import APIRouter, Request, Depends
from fastapi.responses import StreamingResponse

from app.backend.models.chat import Message
from app.backend.services.chat_service import generate_chat_response
from app.backend.services.auth_service import get_current_user

router = APIRouter()

@router.post("/chat", tags=["chat"])
async def chat(
    request: Request,
    message: Message,
    current_user: dict = Depends(get_current_user)
):
    # get global session manager from app state
    session_manager = request.app.state.session_manager

    # get global bot instance from app state
    bot = request.app.state.bot

    # get the chat history instance for the current user session
    chat_history = session_manager.get_or_create_history(str(current_user["id"]))

    # generate and return the chat response as a streaming response
    return StreamingResponse(
        await generate_chat_response(bot, chat_history, message.content),
        media_type="application/json"
    )