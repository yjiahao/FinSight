from fastapi import FastAPI

from app.backend.api.endpoints.v1 import router
from app.backend.core.config import settings

app = FastAPI(title=settings.app_name)
app.include_router(router)