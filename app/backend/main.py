from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.backend.api.endpoints.v1 import router
from app.backend.core.config import settings

from app.backend.services.session_manager import SessionManager

# add app lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # load state variables

    # create a global instance of the session manager
    app.state.session_manager = SessionManager()
    
    # TODO: currently we are creating a new ChatHistory for each session, meaning the embedding model will be loaded multiple times.
    #       we should consider using a shared instance of the embedding model and chat history to save resources.
    #       this will require some refactoring of the ChatHistory class to allow for shared instances
    yield

    # clean up and release the resources
    del app.state.session_manager

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