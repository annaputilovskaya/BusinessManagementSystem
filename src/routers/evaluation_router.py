from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.auth.dependencies import current_active_verified_user, http_bearer
from src.models import Task, User, dbh
from src.schemas.evaluation_schemas import EvaluationCreateSchema, EvaluationReadSchema
from src.services import evaluation_services
from src.services.dependencies import get_task_by_id_manager

router = APIRouter(
    prefix="/evaluations", tags=["Evaluations"], dependencies=[Depends(http_bearer)]
)


@router.post(
    "/{task_id}",
    summary="Create a new evaluation.",
    response_model=EvaluationReadSchema,
)
async def create_evaluation(
    evaluation_in: EvaluationCreateSchema,
    task: Task = Depends(get_task_by_id_manager),
    session: AsyncSession = Depends(dbh.session_getter),
):
    return await evaluation_services.add_evaluation(evaluation_in, task, session)


@router.get("/all/{user_id}", summary="Show user's evaluations.")
async def get_evaluations(
    executor_id: Annotated[UUID, Path],
    session: AsyncSession = Depends(dbh.session_getter),
    user: User = Depends(current_active_verified_user),
    start_date: date | None = None,
    end_date: date | None = None,
):
    return await evaluation_services.get_user_evaluations(
        executor_id, session, user, start_date, end_date
    )


@router.get("/average/{user_id}", summary="Show user's average.")
async def get_average_evaluation(
    executor_id: Annotated[UUID, Path],
    session: AsyncSession = Depends(dbh.session_getter),
    user: User = Depends(current_active_verified_user),
    start_date: date | None = None,
    end_date: date | None = None,
):
    return await evaluation_services.get_user_average_evaluation(
        executor_id, session, user, start_date, end_date
    )


@router.patch(
    "/{task_id}", summary="Update evaluation.", response_model=EvaluationReadSchema
)
async def update_evaluation(
    evaluation_in: EvaluationCreateSchema,
    task: Task = Depends(get_task_by_id_manager),
    session: AsyncSession = Depends(dbh.session_getter),
):
    return await evaluation_services.change_evaluation(evaluation_in, task, session)


@router.delete(
    "/{task_id}", summary="Delete evaluation.", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_evaluation(
    task: Task = Depends(get_task_by_id_manager),
    session: AsyncSession = Depends(dbh.session_getter),
):
    return await evaluation_services.remove_evaluation(task, session)
