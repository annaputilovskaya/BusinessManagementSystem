from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Evaluation, Task
from src.schemas.evaluation_schemas import EvaluationCreateSchema


async def add_evaluation(
        evaluation_in: EvaluationCreateSchema,
        task: Task,
        session: AsyncSession,
) -> Evaluation:
    """
    Adds a new evaluation to the task if it has status done.

    Args:
        evaluation_in (EvaluationCreateSchema): The evaluation data to be created.
        task (Task): The task to which the evaluation will be added.
        session (AsyncSession): The asynchronous database session for committing changes.

    Returns:
        Evaluation: The newly created evaluation object.

    Raises:
        HTTPException:
            - 409 Conflict: If an evaluation already exists for the task.
            - 404 Not Found: If the task status is not "done".

     """
    if task.evaluation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": "An evaluation for the task already exists."}
        )
    elif task.status is "done":
        new_evaluation = Evaluation(
            number=evaluation_in.number,
            task_id=task.id
        )
        session.add(new_evaluation)
        await session.commit()
        await session.refresh(new_evaluation)
        return new_evaluation
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "No done tasks found."}
        )
