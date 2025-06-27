from fastapi import APIRouter

router = APIRouter()

@router.get("/", tags=["home"])
async def root():
    return {"message": "Hello from router!"}