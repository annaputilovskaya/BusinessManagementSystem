from datetime import date, timedelta

import pytest
from fastapi import HTTPException

from src.models import User
from src.services.schedule_services import group_by_date
from src.services.task_services import get_filtered_user_tasks

FUTURE_DATE = date.today() + timedelta(days=7)


async def test_daily_schedule_contains_task_and_meeting(
    client, make_team, make_user, make_task, login
):
    team = await make_team()
    executor = await make_user(team_id=team.id)
    mate = await make_user(team_id=team.id)
    task = await make_task(team_id=team.id, user_id=executor.id, deadline=FUTURE_DATE)
    headers = login(executor)
    client.post(
        "/meetings/",
        json={
            "meet_date": str(FUTURE_DATE),
            "meet_time": "10:00",
            "participants": [str(mate.id)],
        },
        headers=headers,
    )

    resp = client.get(
        "/schedule/day", params={"day": str(FUTURE_DATE)}, headers=headers
    )
    assert resp.status_code == 200, resp.text
    day = resp.json()[str(FUTURE_DATE)]
    assert any(t["id"] == str(task.id) for t in day["tasks"])
    assert len(day["meetings"]) == 1


async def test_monthly_schedule(client, make_team, make_user, make_task, login):
    team = await make_team()
    executor = await make_user(team_id=team.id)
    await make_task(team_id=team.id, user_id=executor.id, deadline=FUTURE_DATE)
    headers = login(executor)
    resp = client.get(
        "/schedule/month",
        params={"day": str(FUTURE_DATE)},
        headers=headers,
    )
    assert resp.status_code == 200
    assert str(FUTURE_DATE) in resp.json()


def test_group_by_date_sorts_meetings_by_time():
    class M:
        def __init__(self, d, t):
            self.meet_date = d
            self.meet_time = t
            self.tasks = []

    day = date(2030, 1, 10)
    meetings = [
        M(day, "14:00"),
        M(day, "09:00"),
    ]
    result = group_by_date(meetings, [])
    assert result[day]["meetings"][0].meet_time == "09:00"


async def test_filtered_tasks_invalid_period_raises():
    with pytest.raises(HTTPException) as exc:
        await get_filtered_user_tasks(
            start_date=date(2030, 2, 1),
            end_date=date(2030, 1, 1),
            session=None,
            user=User(id=None),
        )
    assert exc.value.status_code == 400
