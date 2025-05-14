from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import current_active_verified_superuser
from src.models import dbh, User
from src.schemas.team_schemas import TeamRead
from src.services.team_services import add_team

http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(prefix="/teams", tags=["Teams"], dependencies=[Depends(http_bearer)])


@router.post("/", summary="Create a new team.", response_model=TeamRead)
async def create_team(
        session: AsyncSession = Depends(dbh.session_getter),
        user: User = Depends(current_active_verified_superuser),
):
    return await add_team(session, user)
