from datetime import date, timedelta

FUTURE_DATE = date.today() + timedelta(days=7)


async def test_create_meeting_with_two_teammates(
    client, make_team, make_user, login
):
    team = await make_team()
    creator = await make_user(team_id=team.id)
    mate = await make_user(team_id=team.id)
    headers = login(creator)
    resp = client.post(
        "/meetings/",
        json={
            "meet_date": str(FUTURE_DATE),
            "meet_time": "10:00",
            "participants": [str(mate.id)],
        },
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert len(body["participants"]) == 2


async def test_meeting_conflict_within_one_hour(
    client, make_team, make_user, login
):
    team = await make_team()
    creator = await make_user(team_id=team.id)
    mate = await make_user(team_id=team.id)
    headers = login(creator)
    payload = {
        "meet_date": str(FUTURE_DATE),
        "participants": [str(mate.id)],
    }
    resp = client.post(
        "/meetings/", json={**payload, "meet_time": "10:00"}, headers=headers
    )
    assert resp.status_code == 200, resp.text

    resp = client.post(
        "/meetings/", json={**payload, "meet_time": "10:30"}, headers=headers
    )
    assert resp.status_code == 409, resp.text


async def test_meeting_without_teammates_fails(
    client, make_team, make_user, login
):
    team = await make_team()
    creator = await make_user(team_id=team.id)
    headers = login(creator)
    resp = client.post(
        "/meetings/",
        json={
            "meet_date": str(FUTURE_DATE),
            "meet_time": "11:00",
            "participants": [],
        },
        headers=headers,
    )
    assert resp.status_code == 404, resp.text


async def test_cancel_meeting(
    client, make_team, make_user, login
):
    team = await make_team()
    creator = await make_user(team_id=team.id)
    mate = await make_user(team_id=team.id)
    headers = login(creator)
    resp = client.post(
        "/meetings/",
        json={
            "meet_date": str(FUTURE_DATE),
            "meet_time": "14:00",
            "participants": [str(mate.id)],
        },
        headers=headers,
    )
    meeting_id = resp.json()["id"]

    resp = client.patch(f"/meetings/{meeting_id}", headers=headers)
    assert resp.status_code == 204, resp.text

    resp = client.patch(f"/meetings/{meeting_id}", headers=headers)
    assert resp.status_code == 404


async def test_get_filtered_meetings_invalid_period(
    client, make_team, make_user, login
):
    team = await make_team()
    user = await make_user(team_id=team.id)
    headers = login(user)
    resp = client.get(
        "/meetings/",
        params={"start_date": str(FUTURE_DATE), "end_date": "2020-01-01"},
        headers=headers,
    )
    assert resp.status_code == 400
