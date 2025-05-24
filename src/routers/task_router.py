from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import current_active_verified_user, http_bearer
from src.models import dbh, User
from src.schemas.task_schemas import TaskCreate, TaskRead
from src.services import task_services

router = APIRouter(prefix="/tasks", tags=["Tasks"], dependencies=[Depends(http_bearer)])


@router.post("/", summary="Create a new task.", response_model=TaskRead)
async def create_task(
        task_in: TaskCreate,
        session: AsyncSession = Depends(dbh.session_getter),
        user: User = Depends(current_active_verified_user),
):
    return await task_services.add_task(task_in, session, user)
