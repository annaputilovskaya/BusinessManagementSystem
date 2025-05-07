from fastapi import APIRouter

from src.routers.user_routers import router as user_routers

router = APIRouter()

router.include_router(user_routers)