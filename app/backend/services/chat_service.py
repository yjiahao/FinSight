import json

from typing import AsyncGenerator

from fastapi import Request

async def generate_chat_response(request: Request, message: str) -> AsyncGenerator[str, None]:
    '''
    Service function to generate chat response asynchronously.

    Args:
        message (str): The input message to generate a response for.
    
    Returns:
        AsyncGenerator[str, None]: An asynchronous generator yielding JSON strings
        containing the response tokens.
    '''
    async def response_generator():
        bot = request.app.state.bot
        async for token in bot.prompt(message):
            yield json.dumps({"response": token}) + "\n"
    return response_generator()