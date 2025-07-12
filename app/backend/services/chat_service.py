import json

from typing import AsyncGenerator

from app.backend.chatbot.ChatHistory import ChatHistory
from app.backend.chatbot.InvestingChatBot import InvestingChatBot
from app.backend.speech_to_text.speech_to_text import SpeechToText

async def generate_chat_response(
    bot: InvestingChatBot,
    chat_history: ChatHistory,
    message: str
) -> AsyncGenerator[str, None]:
    '''
    Service function to generate chat response asynchronously.

    Args:
        message (str): The input message to generate a response for.
    
    Returns:
        AsyncGenerator[str, None]: An asynchronous generator yielding JSON strings
        containing the response tokens.
    '''
    async def response_generator():
        async for token in bot.prompt(message, chat_history):
            yield json.dumps({"response": token}) + "\n"
    return response_generator()

async def generate_chat_response_audio(
    bot: InvestingChatBot,
    chat_history: ChatHistory,
    speech_to_text_service: SpeechToText,
    filename: str,
    audio_file: bytes
) -> AsyncGenerator[str, None]:
    '''
    Service function to handle audio messages and generate chat responses asynchronously.

    Args:
        audio_file (bytes): The audio file content to process.
    
    Returns:
        AsyncGenerator[str, None]: An asynchronous generator yielding JSON strings
        containing the response tokens.
    '''
    # transcribe the audio file to text
    transcription: str = speech_to_text_service.transcribe(audio_file, filename)

    async def response_generator():
        # First yield the transcription to the frontend
        yield json.dumps({"response": transcription, "role": "user"}) + "\n"

        # Then yield the bot response tokens
        async for token in bot.prompt(transcription, chat_history):
            yield json.dumps({"response": token, "role": "assistant"}) + "\n"
    return response_generator()