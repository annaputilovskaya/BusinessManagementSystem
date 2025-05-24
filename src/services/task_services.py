from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User, Task
from src.schemas.task_schemas import TaskCreate


async def add_task(
        task_in: TaskCreate,
        session: AsyncSession,
        user: User
) -> Task:
    """
    Add a new task to the database.

    Args:
        task_in (TaskCreate): The input details of the task to be created.
        session (AsyncSession): The database session for executing the operation.
        user (User): The user associated with the task creation.

    Returns:
        Task: The created Task object.

    Raises:
        HTTPException: If the user does not have the necessary permissions
            to access the teams, a 403 Forbidden error is raised.
    """

    if user and user.is_manager:
        if task_in.user_id:
            executor = await session.scalar(select(User).where(User.id == task_in.user_id, User.team_id == user.team_id))
            if executor:
                new_task = Task(
                    name=task_in.name,
                    description=task_in.description,
                    deadline=task_in.deadline,
                    team_id=user.team_id,
                    user_id=executor.id                )
            else:
                new_task = Task(
                    name=task_in.name,
                    description=task_in.description,
                    deadline=task_in.deadline,
                    team_id=user.team_id
                )
        else:
            new_task = Task(
                name=task_in.name,
                description=task_in.description,
                deadline=task_in.deadline,
                team_id=user.team_id,
            )
        session.add(new_task)
        await session.commit()
        await session.refresh(new_task)
        return new_task
    else:
        raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "Not enough permissions for the action."}
        )


async def get_all_tasks(
        session: AsyncSession,
        user: User
) -> list[Task]:
    """
    Retrieve all tasks associated with a specific user.

    Args:
        session (AsyncSession): The database session to be used for querying.
        user (User): The user for whom tasks are to be retrieved.

    Returns:
        list[Task]: A list of Task objects associated with the specified user.

    Raises:
        HTTPException: If the user does not have the necessary permissions
            to access the teams, a 403 Forbidden error is raised.
    """
    if user:
        if user.is_manager:
            tasks = await session.scalars(select(Task).where(Task.team_id == user.team_id))
        else:
            tasks = await session.scalars(select(Task).where(Task.user_id == user.id))
        return list(tasks)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "Not enough permissions for the action."}
        )
