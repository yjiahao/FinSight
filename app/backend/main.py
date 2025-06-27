from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.backend.api.endpoints.v1 import router
from app.backend.core.config import settings

from app.backend.chatbot.InvestingChatBot import InvestingChatBot

# add app lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # load chatbot
    # TODO: change session id in the future to be dynamic
    bot = InvestingChatBot(session_id='1234')  # hardcode session id for now
    app.state.bot = bot
    yield

    # clean up and release the resources
    del app.state.bot

# declare origins for CORS
origins = [
    "http://localhost:8000",
    "http://localhost:5173"
]

app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
)
app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)