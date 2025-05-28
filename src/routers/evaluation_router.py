from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import http_bearer
from src.models import Task, dbh
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
