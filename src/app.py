from fastapi import FastAPI
from pydantic import BaseModel

from InvestingChatBot import InvestingChatBot

app = FastAPI()
bot = InvestingChatBot(session_id='1234') # hardcode session id for now

class Message(BaseModel):
    content: str

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/chat/")
async def chat(message: Message):
    response = bot.prompt(message.content)
    return {"response": response}