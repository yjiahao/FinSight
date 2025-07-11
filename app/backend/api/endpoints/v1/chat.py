from fastapi import APIRouter, Request, Depends
from fastapi.responses import StreamingResponse
from fastapi import File, UploadFile

from langchain.schema import HumanMessage, AIMessage

from app.backend.models.chat import Message
from app.backend.services.chat_service import generate_chat_response, generate_chat_response_audio
from app.backend.services.auth_service import get_current_user

router = APIRouter()

# endpoint to post to for generating chat responses
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

# endpoint to post to for taking in audio messages and generating chat responses
@router.post("/chat/audio", tags=["chat"])
async def chat_audio(
    request: Request,
    audio_file: UploadFile,
    current_user: dict = Depends(get_current_user)
):
    '''
    Handle audio messages from user and generate chat responses.

    Args:
        audio_file (UploadFile): The audio file uploaded by the user.

    Returns:
        StreamingResponse: An asynchronous generator yielding JSON strings
    '''

    # read audio file contents
    audio_contents: bytes = await audio_file.read()
    filename: str = audio_file.filename

    # get global session manager from app state
    session_manager = request.app.state.session_manager

    # get global bot instance from app state
    bot = request.app.state.bot

    # Get the chat history instance for the current user session
    chat_history = session_manager.get_or_create_history(str(current_user["id"]))

    # Get the global speech to text service instance
    speech_to_text_service = request.app.state.speech_to_text_service

    # Generate and return the chat response as a streaming response
    return StreamingResponse(
        await generate_chat_response_audio(
            bot,
            chat_history,
            speech_to_text_service,
            filename, # file name in string
            audio_contents # audio contents in bytes
        ),
        media_type="application/json"
    )

# endpoint to get the chat history for the current user session
@router.get("/chat/history")
async def get_chat_history(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Get user's chat history for frontend display."""
    session_manager = request.app.state.session_manager
    # Use user ID from JWT token instead of session ID
    chat_history = session_manager.get_or_create_history(str(current_user["id"]))
    
    # Get messages from RedisChatMessageHistory (for persistence)
    messages = []
    for msg in chat_history.chat_message_history.messages:
        messages.append({
            "role": "user" if isinstance(msg, HumanMessage) else "assistant",
            "content": msg.content,
            "timestamp": getattr(msg, 'timestamp', None)
        })
    
    return {"messages": messages}

# endpoint to clear chat history for the current user session
@router.delete("/chat/history")
async def clear_chat_history(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Clear user's chat history."""
    session_manager = request.app.state.session_manager
    # Use user ID from JWT token instead of session ID
    session_manager.clear_history(str(current_user["id"]))
    
    return {"message": "Chat history cleared successfully."}