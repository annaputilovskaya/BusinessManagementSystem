import json as jsonlib
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Path, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import (
    authenticate_websocket,
    current_active_verified_user,
    http_bearer,
)
from src.models import Task, User, dbh
from src.schemas.task_schemas import (
    CommentCreate,
    TaskCreate,
    TaskModify,
    TaskRead,
    TaskUpdate,
)
from src.services import dependencies, task_services
from src.services.connection_manager import manager
from src.services.dependencies import get_team_task_by_id
from src.services.task_services import add_comment

router = APIRouter(prefix="/tasks", tags=["Tasks"])
http_auth = [Depends(http_bearer)]


@router.post(
    "/",
    summary="Create a new task.",
    response_model=TaskRead,
    dependencies=http_auth,
)
async def create_task(
    task_in: TaskCreate,
    session: AsyncSession = Depends(dbh.session_getter),
    user: User = Depends(current_active_verified_user),
):
    return await task_services.add_task(task_in, session, user)


@router.get(
    "/",
    summary="Show all tasks.",
    response_model=list[TaskRead],
    dependencies=http_auth,
)
async def get_tasks(
    session: AsyncSession = Depends(dbh.session_getter),
    user: User = Depends(current_active_verified_user),
):
    return await task_services.get_all_tasks(session, user)


@router.get(
    "/{task_id}",
    summary="Show task.",
    response_model=TaskRead,
    dependencies=http_auth,
)
async def get_task(
    task_id: Annotated[UUID, Path],
    session: AsyncSession = Depends(dbh.session_getter),
    user: User = Depends(current_active_verified_user),
):
    return await task_services.get_task_by_id(task_id, session, user)


@router.patch(
    "/{task_id}",
    summary="Change task.",
    response_model=TaskRead,
    dependencies=http_auth,
)
async def modify_task(
    task_in: TaskModify,
    task: Task = Depends(dependencies.get_task_by_id_manager),
    session: AsyncSession = Depends(dbh.session_getter),
    user: User = Depends(current_active_verified_user),
):
    return await task_services.change_task(task_in, task, session, user)


@router.patch(
    "/{task_id}/status",
    summary="Change status.",
    response_model=TaskRead,
    dependencies=http_auth,
)
async def update_task(
    task_in: TaskUpdate,
    task: Task = Depends(dependencies.get_task_by_id_executor),
    session: AsyncSession = Depends(dbh.session_getter),
):
    return await task_services.progress_task(task_in, task, session)


@router.delete(
    "/{task_id}",
    summary="Delete task.",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=http_auth,
)
async def delete_task(
    task: Task = Depends(dependencies.get_task_by_id_manager),
    session: AsyncSession = Depends(dbh.session_getter),
):
    return await task_services.remove_task(task, session)


@router.websocket("/{task_id}/comments/")
async def comment(
    websocket: WebSocket,
    task_id: UUID,
    session: AsyncSession = Depends(dbh.session_getter),
):
    await websocket.accept()
    user = await authenticate_websocket(websocket, session)
    if user is None:
        return
    task = await get_team_task_by_id(task_id, session, user)
    if task is None:
        await websocket.close(code=1008, reason="No task found.")
        return

    manager.connect(task_id=task_id, user_id=user.id, websocket=websocket)
    history = [
        {
            "type": "comment",
            "user_id": str(comment.user_id),
            "text": comment.text,
            "created_at": comment.created_at.isoformat(),
        }
        for comment in task.comments
    ]
    await websocket.send_json(history)
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = jsonlib.loads(raw)
                text = data["text"]
                if not isinstance(text, str):
                    raise TypeError("text must be a string")
            except (
                jsonlib.JSONDecodeError,
                TypeError,
                KeyError,
                AttributeError,
            ):
                await websocket.send_json(
                    {"type": "error", "message": "Invalid message format."}
                )
                continue
            comment_in = CommentCreate(text=text)
            saved = await add_comment(comment_in, task_id, session, user)
            await manager.broadcast(
                task_id,
                {
                    "type": "comment",
                    "user_id": str(saved.user_id),
                    "text": saved.text,
                    "created_at": saved.created_at.isoformat(),
                },
            )
    except WebSocketDisconnect:
        manager.disconnect(task_id=task_id, user_id=user.id)
