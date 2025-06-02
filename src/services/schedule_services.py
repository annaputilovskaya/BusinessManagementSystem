from asyncio import gather
from collections import defaultdict
from datetime import date
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User, Meeting, Task
from src.services.meeting_services import get_filtered_user_meetings
from src.services.task_services import get_filtered_user_tasks


def group_by_date(
        meetings: list[Meeting],
        tasks: list[Task]
) -> dict[date, dict[str, Any] | None]:
    """
    Groups meetings and tasks by their dates.

    Takes two lists with meeting objects and
    with task objects, and organizes them into a
    dictionary where each key is a date and the value is a dictionary
    containing two lists: one for meetings and one for tasks.
    Meetings are sorted by their time within each date.

    Args:
        meetings (list[Meeting]): A list of Meeting objects to be grouped.
        tasks (list[Task]): A list of Task objects to be grouped.

    Returns:
        dict: A dictionary where the keys are dates
        and the values are dictionaries with the keys 'meetings' and
        'tasks', containing lists of the corresponding meeting and task
        objects.
    """
    events_by_date = defaultdict(lambda: {'tasks': [], 'meetings': []})
    for meeting in meetings:
        events_by_date[meeting.meet_date]['meetings'].append(meeting)
    for day in events_by_date:
        events_by_date[day]['meetings'].sort(key=lambda m: (m.meet_time, m.meet_date))
    for task in tasks:
        events_by_date[task.deadline]['tasks'].append(task)
    events_by_date = dict(sorted(events_by_date.items()))
    return events_by_date



async def get_user_schedule(
    start_date: date,
    end_date: date,
    session: AsyncSession,
    user: User
) -> dict[date, dict[str, Any] | None]:
    """
    Retrieve a combined list of meetings and tasks for a user within a specified date range,
    grouped by days.

    Args:
        start_date (date): The start date for filtering meetings and tasks.
        end_date (date): The end date for filtering meetings and tasks.
        session (AsyncSession): The asynchronous database session to use for database operations.
        user (User): The user whose meetings and tasks are to be retrieved.

    Returns:
        dict: A dictionary with dates as keys and nested dictionaries with lists of tasks and meetings.

    Raises:
        HTTPException:
        - 400 Bad Request: if the date range is invalid.
        - 403 Forbidden: if the user does not have the necessary permissions to access.
    """
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Incorrect dates interval."},
        )

    meetings_future = get_filtered_user_meetings(start_date, end_date, session, user)
    tasks_future = get_filtered_user_tasks(start_date, end_date, session, user)
    meetings, tasks = await gather(meetings_future, tasks_future)
    return group_by_date(meetings, tasks)
