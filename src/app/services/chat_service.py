import json
from app.chatbot import bot

async def generate_chat_response(message: str):
    async def response_generator():
        async for token in bot.prompt(message):
            yield json.dumps({"response": token}) + "\n"
    return response_generator()