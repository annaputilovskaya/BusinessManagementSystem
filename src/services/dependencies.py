from typing import Annotated

from fastapi import HTTPException, Path, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.auth.dependencies import current_active_verified_user
from src.models import User, dbh
from src.models.team import Team


async def get_team_by_id(
        team_id: Annotated[int, Path],
        session: AsyncSession = Depends(dbh.session_getter),
        user: User = Depends(current_active_verified_user)
) -> Team:
    """
    Retrieve a team from the database by its ID.

    Retrieves a specific Team object from the database
    based on the provided team ID if the user has the necessary permissions.

    Args:
        team_id (Annotated[int, Path]): The ID of the team to retrieve.
        session (AsyncSession): The database asynchronous session to use for the operation.
        user (User, optional): The currently active verified user.

    Returns:
        Team: The Team object associated with the specified team ID.

    Raises:
        HTTPException: If the user does not have the necessary permissions
        to access the team, a 403 Forbidden error is raised.
    """
    if user:
        return await session.scalar(select(Team).where(Team.id == team_id))
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "Not enough permissions for the action."}
        )
