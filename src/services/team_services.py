from fastapi import HTTPException, status
from sqlalchemy import select, update
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


async def add_team_id_to_team_members(
        user_ids: list[int],
        team: Team,
        session: AsyncSession,
        user: User,
) -> dict[str, str]:
    """Assign a team ID to multiple user members in the database.

    Updates the team ID for a list of users, associating
    them with the specified team, assuming the user has the necessary permissions.

    Args:
        user_ids (list[int]): A list of user IDs to be updated with the team ID.
        team (Team): The Team object that the users will be associated with.
        session (AsyncSession): The database asynchronous session to use for the operation.
        user (User): The user requesting the update, must have the required permissions.

    Returns:
        dict[str, str]: A dictionary indicating the result of the update with a detail message.

    Raises:
        HTTPException:
            - If the user does not have the necessary permissions, a 403 Forbidden error is raised.
            - If no users are found for the provided user IDs, a 404 Not Found error is raised.
            - If the specified team is not found, a 404 Not Found error is raised.
    """

    if user:
        if team:
            users_update = await session.scalars(select(User).where(User.id.in_(user_ids)))
            if users_update is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={"message": "No users found."}
                )
            else:
                await session.execute(update(User).where(User.id.in_(user_ids)).values(team_id=team.id))
                await session.commit()
                return {"detail": "Team updated."}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": "No team found."}
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "Not enough permissions for the action."}
        )


async def remove_team(
        team: Team,
        session: AsyncSession,
        user: User
) -> dict[str, str]:
    """
    Remove a team from the database.

    Deletes the specified Team object from the database
    if the user has the necessary permissions.

    Args:
        team (Team): The Team object to be deleted.
        session (AsyncSession): The database asynchronous session to use for the operation.
        user (User): The user requesting the deletion. Must have the required permissions.

    Returns:
        dict[str, str]: A dictionary indicating the result of the deletion with a detail message.

    Raises:
        HTTPException:
            - If the user does not have the necessary permissions, a 403 Forbidden error is raised.
            - If the specified team is not found, a 404 Not Found error is raised.
    """
    if user:
        if team:
            await session.delete(team)
            await session.commit()
            return {"detail": "Team deleted."}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": "No team found."}
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "Not enough permissions for the action."}
        )
