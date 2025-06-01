from typing import Annotated

from fastapi import HTTPException, Path, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import current_active_verified_user
from src.models import User, dbh, Task, Team
from src.models.meeting import Meeting


async def get_team_by_id(
        team_id: Annotated[int, Path],
        session: AsyncSession = Depends(dbh.session_getter),
        user: User = Depends(current_active_verified_user)
) -> Team:
    """
    Retrieve a team from the database by ID.

    Retrieves a specific Team object from the database
    based on the provided team ID if the user has the necessary permissions.

    Args:
        team_id (Annotated[int, Path]): The ID of the team to retrieve.
        session (AsyncSession): The database asynchronous session to use for the operation.
        user (User, optional): The currently active verified user.

    Returns:
        Team: The Team object associated with the specified team ID.

    Raises:
            HTTPException:
            - 403 Forbidden: if the user does not have the necessary permissions.
            - 404 Not Found: if the specified team is not found.
    """

    if user:
        team = await session.scalar(select(Team).where(Team.id == team_id))
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": "No teams found."}
            )
        return team
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "Not enough permissions for the action."}
        )


async def get_task_by_id_executor(
        task_id: Annotated[int, Path],
        session: AsyncSession = Depends(dbh.session_getter),
        user: User = Depends(current_active_verified_user)
) -> Task:
    """
    Retrieve a task from the database by ID if user is not a manager.

    Args:
        task_id (int): The ID of the task to retrieve.
        session (AsyncSession): The database session to be used for querying.
        user (User): The user for whom tasks are to be retrieved.

    Returns:
        Task: A Task object associated with the specified task ID.

    Raises:
        HTTPException:
        - 403 Forbidden: if the user is not an active verified user.
        - 404 Not found: if the user does not have the necessary permissions to access the task,
            or task with such ID does not exist in the database.
    """
    if user:
        task = await session.scalar(select(Task).where(Task.id == task_id, Task.user_id == user.id))
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": "No tasks found."}
            )
        return task
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "Not enough permissions for the action."}
        )


async def get_task_by_id_manager(
        task_id: Annotated[int, Path],
        session: AsyncSession = Depends(dbh.session_getter),
        user: User = Depends(current_active_verified_user)
) -> Task:
    """
    Retrieve a task from the database by ID if user is a manager.

    Args:
        task_id (int): The ID of the task to retrieve.
        session (AsyncSession): The database session to be used for querying.
        user (User): The user for whom tasks are to be retrieved.

    Returns:
        Task: A Task object associated with the specified task ID.

    Raises:
        HTTPException:
        - 403 Forbidden: if the user is not an active verified user.
        - 404 Not found: if the user does not have the necessary permissions to access the task,
            or task with such ID does not exist in the database.
    """
    if user and user.is_manager:
        task = await session.scalar(select(Task).where(Task.id == task_id, Task.team_id == user.team_id))
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": "No tasks found."}
            )
        return task
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "Not enough permissions for the action."}
        )


async def get_meeting_by_id(
        meeting_id: Annotated[int, Path],
        session: AsyncSession = Depends(dbh.session_getter),
        user: User = Depends(current_active_verified_user)
) -> Meeting:
    """
    Retrieve a meeting from the database by ID if user is a participant of the meeting.

    Show meeting if it's not canceled.

    Args:
        meeting_id (int): The ID of the meeting to retrieve.
        session (AsyncSession): The database session to be used for querying.
        user (User): The user for whom meeting are to be retrieved.

    Returns:
        Meeting: A Meeting object associated with the specified meeting ID.

    Raises:
        HTTPException:
        - 403 Forbidden: if the user is not an active verified user.
        - 404 Not found: if the user does not have the necessary permissions to access the meeting,
            or meeting with such ID does not exist in the database.
    """

    meeting_db = await session.scalar(select(Meeting).where(
        Meeting.id == meeting_id,
        Meeting.is_canceled == False,
        Meeting.participants.any(User.id == user.id)
    ))
    if not meeting_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "No meetings found."}
        )
    return meeting_db
