from fastapi import APIRouter

from src.routers.user_router import router as user_router
from src.routers.team_router import router as team_router
from src.routers.task_router import router as task_router
from src.routers.evaluation_router import router as evaluation_router
from src.routers.meeting_router import router as meeting_router



router = APIRouter()

router.include_router(user_router)
router.include_router(team_router)
router.include_router(task_router)
router.include_router(evaluation_router)
router.include_router(meeting_router)