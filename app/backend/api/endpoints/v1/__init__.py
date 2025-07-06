from fastapi import APIRouter
from . import home, chat, auth

router = APIRouter()

router.include_router(home.router)
router.include_router(chat.router)
router.include_router(auth.router)