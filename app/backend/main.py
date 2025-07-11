from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.backend.api.endpoints.v1 import router
from app.backend.core.config import settings

from app.backend.services.session_manager import SessionManager
from app.backend.chatbot.InvestingChatBot import InvestingChatBot
from app.backend.speech_to_text.speech_to_text import SpeechToTextService

from dotenv import load_dotenv

load_dotenv()

# add app lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # load state variables

    # create a global instance of the session manager
    app.state.session_manager = SessionManager()

    # create global instance of bot, which is stateless and can be shared across sessions
    app.state.bot = InvestingChatBot()

    # create global instance of speech to text service
    app.state.speech_to_text_service = SpeechToTextService()
    
    yield

    # clean up and release the resources
    del app.state.session_manager
    del app.state.bot
    del app.state.speech_to_text_service

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