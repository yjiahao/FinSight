from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.backend.api.endpoints.v1 import router
from app.backend.core.config import settings

# declare origins for CORS
origins = [
    "https://localhost:8000",
    "https://localhost:5173"
]

app = FastAPI(title=settings.app_name)
app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)