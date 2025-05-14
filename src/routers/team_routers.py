from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.auth.dependencies import current_active_verified_superuser, current_active_verified_user
from src.models import dbh, User, Team
from src.schemas.team_schemas import TeamRead
from src.services.dependencies import get_team_by_id
from src.services.team_services import add_team, get_all_teams, add_team_id_to_team_members, remove_team

http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(prefix="/teams", tags=["Teams"], dependencies=[Depends(http_bearer)])


@router.post("/", summary="Create a new team.", response_model=TeamRead)
async def create_team(
        session: AsyncSession = Depends(dbh.session_getter),
        user: User = Depends(current_active_verified_superuser),
):
    return await add_team(session, user)


@router.get("/", summary="Show all teams.", response_model=list[TeamRead])
async def get_teams(
        session: AsyncSession = Depends(dbh.session_getter),
        user: User = Depends(current_active_verified_user)
):
    return await get_all_teams(session, user)


@router.get("/{team_id}", summary="Show team.", response_model=TeamRead)
async def get_team(
        team: Team = Depends(get_team_by_id)
):
    return team


@router.patch("/{team_id}", summary="Update team members.", status_code=status.HTTP_200_OK)
async def update_team(
        user_ids: list[int],
        team: Team = Depends(get_team_by_id),
        session: AsyncSession = Depends(dbh.session_getter),
        user: User = Depends(current_active_verified_superuser),
):
    return await add_team_id_to_team_members(user_ids, team, session, user)


@router.delete("/{team_id}", summary="Delete team.", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
        team: Team = Depends(get_team_by_id),
        session: AsyncSession = Depends(dbh.session_getter),
        user: User = Depends(current_active_verified_superuser),
):
    return await remove_team(team, session, user)
