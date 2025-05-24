from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import current_active_verified_user, http_bearer
from src.models import dbh, User, Task
from src.schemas.task_schemas import TaskCreate, TaskRead, TaskModify
from src.services import task_services, dependencies

router = APIRouter(prefix="/tasks", tags=["Tasks"], dependencies=[Depends(http_bearer)])


@router.post("/", summary="Create a new task.", response_model=TaskRead)
async def create_task(
        task_in: TaskCreate,
        session: AsyncSession = Depends(dbh.session_getter),
        user: User = Depends(current_active_verified_user),
):
    return await task_services.add_task(task_in, session, user)


@router.get("/", summary="Show all tasks.", response_model=list[TaskRead])
async def get_tasks(
        session: AsyncSession = Depends(dbh.session_getter),
        user: User = Depends(current_active_verified_user)
):
    return await task_services.get_all_tasks(session, user)


@router.get("/{task_id}", summary="Show task.", response_model=TaskRead)
async def get_task(
        task_id: Annotated[int, Path],
        session: AsyncSession = Depends(dbh.session_getter),
        user: User = Depends(current_active_verified_user)):
    return await task_services.get_task_by_id(task_id, session, user)


@router.patch("/{task_id}", summary="Change task.", response_model=TaskRead)
async def modify_task(
        task_in: TaskModify,
        task: Task = Depends(dependencies.get_task_by_id_manager),
        session: AsyncSession = Depends(dbh.session_getter),
        user: User = Depends(current_active_verified_user)
):
    return await task_services.change_task(task_in, task, session, user)
