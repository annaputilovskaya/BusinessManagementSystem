from datetime import date

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import current_active_verified_user, http_bearer
from src.models import Meeting, User, dbh
from src.schemas.meeting_schemas import MeetingCreateSchema, MeetingReadSchema
from src.services import meeting_services
from src.services.dependencies import get_meeting_by_id

router = APIRouter(
    prefix="/meetings", tags=["Meetings"], dependencies=[Depends(http_bearer)]
)


@router.post("/", summary="Create meeting.", response_model=MeetingReadSchema)
async def create_meeting(
    meeting_in: MeetingCreateSchema,
    session: AsyncSession = Depends(dbh.session_getter),
    user: User = Depends(current_active_verified_user),
):
    return await meeting_services.add_meeting(meeting_in, session, user)


@router.get(
    "/",
    summary="Show user meetings per period.",
    response_model=list[MeetingReadSchema],
)
async def get_meetings(
    start_date: date,
    end_date: date,
    session: AsyncSession = Depends(dbh.session_getter),
    user: User = Depends(current_active_verified_user),
):
    return await meeting_services.get_filtered_user_meetings(
        start_date, end_date, session, user
    )


@router.get("/{meeting_id}", summary="Show meeting.", response_model=MeetingReadSchema)
async def get_meeting(
    meeting: Meeting = Depends(get_meeting_by_id),
):
    return meeting


@router.patch(
    "/{meeting_id}", summary="Cancel meeting.", status_code=status.HTTP_204_NO_CONTENT
)
async def cancel_meeting(
    meeting: Meeting = Depends(get_meeting_by_id),
    session: AsyncSession = Depends(dbh.session_getter),
):
    return await meeting_services.cancel_meeting(meeting, session)
