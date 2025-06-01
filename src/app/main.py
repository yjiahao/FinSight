from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

from app.api.endpoints.v1 import router

from app.core.config import settings

import json

app = FastAPI(title=settings.app_name)
app.include_router(router, prefix="/api/v1")

# bot = InvestingChatBot(session_id='1234') # hardcode session id for now
@app.get("/")
async def root():
    return {"message": "Hello World"}