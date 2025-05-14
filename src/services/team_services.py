from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.models import User, Team


async def add_team(session: AsyncSession, user: User) -> Team:
    """
    Add a new team to the database.

    Creates a new Team object and adds it to the database
    if the provided user has the necessary permissions.

    Args:
        session (AsyncSession): The database asynchronous session to use for the operation.
        user (User): The user attempting to add a team. Must have the required permissions.

    Returns:
        Team: The newly created Team object.

    Raises:
        HTTPException: If the user does not have the necessary permissions
        to add a team, a 403 Forbidden error is raised.
    """
    if user:
        new_team = Team()
        session.add(new_team)
        await session.commit()
        await session.refresh(new_team)
        return new_team
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "Not enough permissions for the action."}
        )


async def get_all_teams(session: AsyncSession, user: User) -> list[Team]:
    """
    Retrieve all teams from the database.

    Retrieves a list of all Team objects from the database
    if the provided user has the necessary permissions.

    Args:
        session (AsyncSession): The database session to use for the operation.
        user (User): The user attempting to retrieve the teams. Must have the required permissions.

    Returns:
        list[Team]: A list of Team objects.

    Raises:
        HTTPException: If the user does not have the necessary permissions
        to access the teams, a 403 Forbidden error is raised.
    """
    if user:
        teams = await session.scalars(select(Team))
        return list(teams)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "Not enough permissions for the action."}
        )
