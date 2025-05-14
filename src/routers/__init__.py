from fastapi import APIRouter

from src.routers.user_routers import router as user_routers
from src.routers.team_routers import router as team_routers


router = APIRouter()

router.include_router(user_routers)
router.include_router(team_routers)
