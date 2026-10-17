from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Path, status, WebSocket, BackgroundTasks, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import current_active_verified_user, http_bearer
from src.models import Task, User, dbh
from src.schemas.task_schemas import (
    TaskCreate,
    TaskModify,
    TaskRead,
    TaskUpdate,
)
from src.services import dependencies, task_services
from src.services.connection_manager import manager

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
    user: User = Depends(current_active_verified_user),
):
    return await task_services.get_all_tasks(session, user)


@router.get("/{task_id}", summary="Show task.", response_model=TaskRead)
async def get_task(
    task_id: Annotated[UUID, Path],
    session: AsyncSession = Depends(dbh.session_getter),
    user: User = Depends(current_active_verified_user),
):
    return await task_services.get_task_by_id(task_id, session, user)


@router.patch("/{task_id}", summary="Change task.", response_model=TaskRead)
async def modify_task(
    task_in: TaskModify,
    task: Task = Depends(dependencies.get_task_by_id_manager),
    session: AsyncSession = Depends(dbh.session_getter),
    user: User = Depends(current_active_verified_user),
):
    return await task_services.change_task(task_in, task, session, user)


@router.patch("/{task_id}/status", summary="Change status.", response_model=TaskRead)
async def update_task(
    task_in: TaskUpdate,
    task: Task = Depends(dependencies.get_task_by_id_executor),
    session: AsyncSession = Depends(dbh.session_getter),
):
    return await task_services.progress_task(task_in, task, session)


@router.delete(
    "/{task_id}", summary="Delete task.", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_task(
    task: Task = Depends(dependencies.get_task_by_id_manager),
    session: AsyncSession = Depends(dbh.session_getter),
):
    return await task_services.remove_task(task, session)


@router.websocket("/{task_id}/comments/")
async def comment(
        websocket:WebSocket,
        task_id: UUID,
        session: AsyncSession = Depends(dbh.session_getter),
        user: User = Depends(current_active_verified_user),
):
    comments = await manager.connect(websocket, task_id, session, user)
    try:
        await manager.send_comments_history(websocket, comments)
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data, task_id, session, user, BackgroundTasks)
    except WebSocketDisconnect:
        manager.disconnect(task_id, user)
