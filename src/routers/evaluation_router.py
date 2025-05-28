from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

import src.services
from src.auth.dependencies import http_bearer, current_active_verified_user
from src.models import Task, dbh, User
from src.schemas.evaluation_schemas import EvaluationReadSchema, EvaluationCreateSchema
from src.services.dependencies import get_task_by_id_manager
from src.services import evaluation_services

router = APIRouter(prefix="/evaluations", tags=["Evaluations"], dependencies=[Depends(http_bearer)])


@router.post("/{task_id}", summary="Create a new evaluation.", response_model=EvaluationReadSchema)
async def create_evaluation(
        evaluation_in: EvaluationCreateSchema,
        task: Task = Depends(get_task_by_id_manager),
        session: AsyncSession = Depends(dbh.session_getter)
):
    return await evaluation_services.add_evaluation(evaluation_in, task, session)


@router.get("/all/{user_id}", summary="Show user's evaluations.")
async def get_evaluations(
        executor_id: Annotated[int, Path],
        session: AsyncSession = Depends(dbh.session_getter),
        user: User = Depends(current_active_verified_user),
        start_date: date | None = None,
        end_date: date | None = None,
):
    return await src.services.evaluation_services.get_user_evaluations(
        executor_id, session, user, start_date, end_date
    )
