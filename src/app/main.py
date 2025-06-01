from fastapi import FastAPI

from app.api.endpoints.v1 import router
from app.core.config import settings

app = FastAPI(title=settings.app_name)
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Hello World"}