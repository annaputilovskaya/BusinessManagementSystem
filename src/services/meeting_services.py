from datetime import date, datetime, time, timedelta
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Meeting, MeetingUserAssociation, User
from src.schemas.meeting_schemas import MeetingCreateSchema


async def check_schedule_conflict(
    participant_ids: list[UUID],
    meeting_date: date,
    meeting_time: time,
    session: AsyncSession,
) -> list[Meeting]:
    """
    Checks for scheduling conflicts for a list of participants.

    A conflict is considered to occur if there is a meeting within one hour
    before or after the specified meeting datetime. The check is timezone-free
    and correctly handles the midnight boundary (e.g. a 00:30 meeting conflicts
    with a 23:30 meeting of the previous day).

    Args:
        participant_ids (list[UUID]): A list of participant user IDs to check for conflicts.
        meeting_date (date): The date of the proposed meeting.
        meeting_time (time): The time of the proposed meeting.
        session (AsyncSession): The asynchronous database session to use for querying.

    Returns:
        list[Meeting]: A list of Meeting objects that conflict with the proposed meeting.
    """

    proposed = datetime.combine(meeting_date, meeting_time)
    window_start = proposed - timedelta(hours=1)
    window_end = proposed + timedelta(hours=1)
    candidates = await session.scalars(
        select(Meeting)
        .join(MeetingUserAssociation)
        .where(
            MeetingUserAssociation.user_id.in_(participant_ids),
            Meeting.is_canceled.is_(False),
            Meeting.meet_date.between(window_start.date(), window_end.date()),
        )
    )
    return [
        meeting
        for meeting in candidates
        if window_start
        <= datetime.combine(meeting.meet_date, meeting.meet_time)
        <= window_end
    ]


async def add_meeting(
    meeting_in: MeetingCreateSchema, session: AsyncSession, user: User
) -> Meeting:
    """
    Add a new meeting for a list of participants.

    Attempts to create a new meeting with the specified
    date, time, and participants. It first checks for any scheduling conflicts with
    existing meetings and valid participants in the user's team.

    Args:
        meeting_in (MeetingCreateSchema): The details of the meeting to be created.
        session (AsyncSession): The asynchronous database session to use for database operations.
        user (User): The user requesting to add the meeting, used to verify team membership.

    Returns:
        Meeting: The newly created Meeting object.

    Raises:
        HTTPException:
        - 409 Conflict: if there is a scheduling conflict.
        - 404 Not Found: if no valid participants are found in the user's team.
    """

    meeting_in.participants.append(user.id)
    conflicts = await check_schedule_conflict(
        meeting_in.participants, meeting_in.meet_date, meeting_in.meet_time, session
    )
    if conflicts:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "There is another meeting for one or more participants in the same time."
            },
        )
    else:
        participants = await session.scalars(
            select(User).where(
                User.id.in_(meeting_in.participants), User.team_id == user.team_id
            )
        )
        participants = list(participants)
        if len(participants) == 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": "There are no such users in your team."},
            )
        else:
            new_meeting = Meeting(
                meet_date=meeting_in.meet_date,
                meet_time=meeting_in.meet_time,
                participants=participants,
            )

            session.add(new_meeting)
            await session.commit()
            await session.refresh(new_meeting)
            return new_meeting


async def get_filtered_user_meetings(
    start_date: date,
    end_date: date,
    session: AsyncSession,
    user: User,
) -> list[Meeting]:
    """
    Retrieve a list of meetings for a user within a specified date range.

    Fetches all meetings associated with the specified user
    that fall within the provided start and end dates. Only meetings that are not canceled
    will be included in the results.

    Args:
        start_date (date): The start date for filtering meetings.
        end_date (date): The end date for filtering meetings.
        session (AsyncSession): The asynchronous database session to use for database operations.
        user (User): The user whose meetings are to be retrieved.

    Returns:
        list[Meeting]: A list of Meeting objects that match the user's criteria.

    Raises:
        HTTPException:
        - 400 Bad Request: if the date range is invalid.
    """
    if start_date <= end_date:
        meetings = await session.scalars(
            select(Meeting)
            .join(MeetingUserAssociation)
            .where(
                MeetingUserAssociation.user_id == user.id,
                Meeting.is_canceled.is_(False),
                Meeting.meet_date.between(start_date, end_date),
            )
            .order_by(Meeting.meet_date, Meeting.meet_time)
        )
        return list(meetings)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Incorrect dates interval."},
        )


async def cancel_meeting(
    meeting_db: Meeting,
    session: AsyncSession,
) -> dict[str, str]:
    """
    Cancel an existing meeting in the database.

    Marks the specified meeting as canceled in the database.

    Args:
        meeting_db (Meeting): The Meeting object to be canceled.
        session (AsyncSession): The asynchronous database session used for committing the changes.

    Returns:
        dict[str, str]: A dictionary containing a detail message indicating the meeting has been canceled.
    """
    meeting_db.is_canceled = True
    await session.commit()
    return {"detail": "Meeting canceled."}
