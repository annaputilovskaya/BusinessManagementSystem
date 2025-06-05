from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User, Team


async def add_team(session: AsyncSession) -> Team:
    """
    Add a new team to the database.

    Args:
        session (AsyncSession): The database asynchronous session to use for the operation.

    Returns:
        Team: The newly created Team object.
    """

    new_team = Team()
    session.add(new_team)
    await session.commit()
    await session.refresh(new_team)
    return new_team


async def get_all_teams(session: AsyncSession) -> list[Team]:
    """
    Retrieve all teams from the database.

    Args:
        session (AsyncSession): The database session to use for the operation.

    Returns:
        list[Team]: A list of Team objects.
    """

    teams = await session.scalars(select(Team))
    return list(teams)


async def add_team_id_to_team_members(
    user_ids: list[int],
    team: Team,
    session: AsyncSession,
) -> dict[str, str]:
    """Assign a team ID to multiple user members in the database.

    Updates the team ID for a list of users, associating
    them with the specified team.

    Args:
        user_ids (list[int]): A list of user IDs to be updated with the team ID.
        team (Team): The Team object that the users will be associated with.
        session (AsyncSession): The database asynchronous session to use for the operation.

    Returns:
        dict[str, str]: A dictionary indicating the result of the update with a detail message.

    Raises:
        HTTPException:
            - 404 Not Found: If no users are found for the provided user IDs.
    """

    users_update = await session.scalars(select(User).where(User.id.in_(user_ids)))
    if users_update is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail={"message": "No users found."}
        )
    else:
        await session.execute(
            update(User).where(User.id.in_(user_ids)).values(team_id=team.id)
        )
        await session.commit()
        return {"detail": "Team updated."}


async def remove_team(
    team: Team,
    session: AsyncSession,
) -> dict[str, str]:
    """
    Remove a team from the database.

    Deletes the specified Team object from the database
    if the user has the necessary permissions.

    Args:
        team (Team): The Team object to be deleted.
        session (AsyncSession): The database asynchronous session to use for the operation.

    Returns:
        dict[str, str]: A dictionary indicating the result of the deletion with a detail message.
    """

    await session.delete(team)
    await session.commit()
    return {"detail": "Team deleted."}
