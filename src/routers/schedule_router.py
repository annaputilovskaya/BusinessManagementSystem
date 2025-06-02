from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import http_bearer, current_active_verified_user
from src.models import dbh, User
from src.services.schedule_services import get_user_schedule
from src.services.utils import get_first_and_last_day_of_month

router = APIRouter(prefix="/schedule", tags=["Schedule"], dependencies=[Depends(http_bearer)])


@router.get("/day", summary="Daily schedule.")
async def get_daily_schedule(
        day: date,
        session: AsyncSession = Depends(dbh.session_getter),
        user: User = Depends(current_active_verified_user)
):
    return await get_user_schedule(day, day, session, user)


@router.get("/month", summary="Monthly schedule.")
async def get_monthly_schedule(
        day: date,
        session: AsyncSession = Depends(dbh.session_getter),
        user: User = Depends(current_active_verified_user)
):
    first_day, last_day = get_first_and_last_day_of_month(day)
    return await get_user_schedule(first_day, last_day, session, user)
