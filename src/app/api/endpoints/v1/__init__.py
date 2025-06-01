from fastapi import APIRouter
from . import home, chat

router = APIRouter()
router.include_router(home.router)
router.include_router(chat.router)