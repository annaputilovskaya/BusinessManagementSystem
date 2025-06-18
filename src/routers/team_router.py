from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import (
    current_active_verified_superuser,
    current_active_verified_user,
    http_bearer,
)
from src.models import dbh, User, Team
from src.schemas.team_schemas import TeamRead
from src.services.dependencies import get_team_by_id
from src.services.team_services import (
    add_team,
    get_all_teams,
    add_team_id_to_team_members,
    remove_team,
)

router = APIRouter(prefix="/teams", tags=["Teams"], dependencies=[Depends(http_bearer)])


@router.post("/", summary="Create a new team.", response_model=TeamRead)
async def create_team(
    session: AsyncSession = Depends(dbh.session_getter),
    user: User = Depends(current_active_verified_superuser),
):
    return await add_team(session)


@router.get("/", summary="Show all teams.", response_model=list[TeamRead])
async def get_teams(
    session: AsyncSession = Depends(dbh.session_getter),
    user: User = Depends(current_active_verified_user),
):
    return await get_all_teams(session)


@router.get("/{team_id}", summary="Show team.", response_model=TeamRead)
async def get_team(team: Team = Depends(get_team_by_id)):
    return team


@router.patch(
    "/{team_id}", summary="Update team members.", status_code=status.HTTP_200_OK
)
async def update_team(
    user_ids: list[UUID],
    team: Team = Depends(get_team_by_id),
    session: AsyncSession = Depends(dbh.session_getter),
    user: User = Depends(current_active_verified_superuser),

):
    return await add_team_id_to_team_members(user_ids, team, session)


@router.delete(
    "/{team_id}", summary="Delete team.", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_team(
    team: Team = Depends(get_team_by_id),
    session: AsyncSession = Depends(dbh.session_getter),
    user: User = Depends(current_active_verified_superuser),

):
    return await remove_team(team, session)
