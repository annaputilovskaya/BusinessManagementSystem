from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Evaluation, Task, User
from src.schemas.evaluation_schemas import EvaluationCreateSchema
from src.services.utils import check_dates


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


async def get_user_evaluations(
        executor_id: int,
        session: AsyncSession,
        user: User,
        start_date: date | None = None,
        end_date: date | None = None,
) -> list[int]:
    """
    Retrieves evaluations for a specific user within an optional date range.

    Args:
        executor_id (int): The ID of the user whose evaluations are to be retrieved.
        session (AsyncSession): The asynchronous database session for querying.
        user (User): The current user requesting the evaluations.
        start_date (Optional(date)): The optional start date for filtering evaluations (default is None).
        end_date (Optional(date)): The optional end date for filtering evaluations (default is None).

        Returns:
        list[int]: A list of evaluation numbers for the specified user within the date range.

        Raises:
        HTTPException:
            - 403 Forbidden: If the user does not have sufficient permissions to access the evaluations.
    """

    start_date, end_date = check_dates(start_date, end_date)
    if user and user.id == executor_id:
        stmt = (
            select(Evaluation.number)
            .join(Task)
            .filter(Task.user_id == executor_id)
            .filter(Evaluation.created_at.between(start_date, end_date))
        )
        numbers = await session.scalars(stmt)
        return list(numbers)
    elif user and user.is_manager:
        stmt = (
            select(Evaluation.number)
            .join(Task)
            .filter(Task.team_id == user.team_id)
            .filter(Task.user_id == executor_id)
            .filter(Evaluation.created_at.between(start_date, end_date))
        )
        numbers = await session.scalars(stmt)
        return list(numbers)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "Not enough permissions for the action."}
        )


async def get_user_average_evaluation(
        executor_id: int,
        session: AsyncSession,
        user: User,
        start_date: date | None = None,
        end_date: date | None = None,
) -> float | None:
    """
    Calculates the average evaluation score.

    Retrieves the evaluation numbers for the user specified by the executor_id and
    computes the average of those evaluations rounded to two decimal places. If there are no
    evaluations, it returns None.

    Args:
        executor_id (int): The ID of the user whose average evaluation is to be calculated.
        session (AsyncSession): The asynchronous database session for querying.
        user (User): The current user requesting the average evaluation.
        start_date (Optional(date)): The optional start date for filtering evaluations (default is None).
        end_date (Optional(date)): The optional end date for filtering evaluations (default is None).

    Returns:
        float | None: The average evaluation score rounded to two decimal places, or None if no evaluations exist.
    """
    numbers = await get_user_evaluations(executor_id, session, user, start_date, end_date)
    if numbers:
        return round(sum(numbers)/len(numbers), 2)


async def change_evaluation(
        evaluation_in: EvaluationCreateSchema,
        task: Task,
        session: AsyncSession,
) -> Evaluation:
    """
    Updates an existing evaluation for the task with new data.

    Args:
        evaluation_in (EvaluationCreateSchema): The new evaluation data to update.
        task (Task): The task associated with the evaluation to be changed.
        session (AsyncSession): The asynchronous database session for committing changes.

    Returns:
        Evaluation: The updated evaluation object after changes have been applied.
    """

    evaluation_db = await session.scalar(select(Evaluation).where(Evaluation.task_id == task.id))
    evaluation_db.number = evaluation_in.number
    session.add(evaluation_db)
    await session.commit()
    await session.refresh(evaluation_db)
    return evaluation_db


async def remove_evaluation(
        task: Task,
        session: AsyncSession,
) -> dict[str, str]:
    """
    Removes the evaluation associated with the task.

    Args:
        task (Task): The task for which the evaluation will be removed.
        session (AsyncSession): The asynchronous database session for committing changes.

    Returns:
        dict[str, str]: A dictionary containing a success message indicating that the evaluation was deleted.

    Raises:
        HTTPException:
            - 404 Not Found: If no evaluations are found for the specified task.
    """

    evaluation = await session.scalar(select(Evaluation).where(Evaluation.task_id == task.id))
    if evaluation:
        await session.delete(evaluation)
        await session.commit()
        return {"detail": "Evaluation deleted."}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "No evaluations found."}
        )
