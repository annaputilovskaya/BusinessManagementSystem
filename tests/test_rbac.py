async def test_executor_cannot_create_task(client, make_team, make_user, login):
    team = await make_team()
    executor = await make_user(team_id=team.id)
    headers = login(executor)
    resp = client.post(
        "/tasks/",
        json={
            "name": "T",
            "description": "D",
            "deadline": "2030-01-01",
        },
        headers=headers,
    )
    assert resp.status_code == 403, resp.text


async def test_manager_without_team_cannot_create_task(
    client, make_user, login
):
    manager = await make_user(is_manager=True, team_id=None)
    headers = login(manager)
    resp = client.post(
        "/tasks/",
        json={"name": "T", "description": "D", "deadline": "2030-01-01"},
        headers=headers,
    )
    assert resp.status_code == 403, resp.text


async def test_manager_can_create_task(client, make_team, make_user, login):
    team = await make_team()
    manager = await make_user(is_manager=True, team_id=team.id)
    headers = login(manager)
    resp = client.post(
        "/tasks/",
        json={"name": "T", "description": "D", "deadline": "2030-01-01"},
        headers=headers,
    )
    assert resp.status_code == 200, resp.text


async def test_executor_cannot_delete_task(
    client, make_team, make_user, make_task, login
):
    team = await make_team()
    executor = await make_user(team_id=team.id)
    task = await make_task(team_id=team.id, user_id=executor.id)
    headers = login(executor)
    resp = client.delete(f"/tasks/{task.id}", headers=headers)
    assert resp.status_code == 403, resp.text


async def test_executor_updates_own_task_status(
    client, make_team, make_user, make_task, login
):
    team = await make_team()
    executor = await make_user(team_id=team.id)
    task = await make_task(team_id=team.id, user_id=executor.id)
    headers = login(executor)
    resp = client.patch(
        f"/tasks/{task.id}/status",
        json={"status": "progress"},
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "progress"


async def test_executor_cannot_update_foreign_task_status(
    client, make_team, make_user, make_task, login
):
    team = await make_team()
    executor = await make_user(team_id=team.id)
    other = await make_user(team_id=team.id)
    task = await make_task(team_id=team.id, user_id=other.id)
    headers = login(executor)
    resp = client.patch(
        f"/tasks/{task.id}/status",
        json={"status": "progress"},
        headers=headers,
    )
    assert resp.status_code == 404


async def test_non_superuser_cannot_create_team(client, make_user, login):
    user = await make_user()
    headers = login(user)
    resp = client.post("/teams/", headers=headers)
    assert resp.status_code == 403
