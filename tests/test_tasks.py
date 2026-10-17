async def test_manager_creates_task_with_executor(
    client, make_team, make_user, login
):
    team = await make_team()
    manager = await make_user(is_manager=True, team_id=team.id)
    executor = await make_user(team_id=team.id)
    headers = login(manager)
    resp = client.post(
        "/tasks/",
        json={
            "name": "Task A",
            "description": "desc",
            "deadline": "2030-01-01",
            "user_id": str(executor.id),
        },
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["user"]["id"] == str(executor.id)
    assert body["status"] == "opened"


async def test_task_executor_from_foreign_team_not_assigned(
    client, make_team, make_user, login
):
    team = await make_team()
    other_team = await make_team()
    manager = await make_user(is_manager=True, team_id=team.id)
    outsider = await make_user(team_id=other_team.id)
    headers = login(manager)
    resp = client.post(
        "/tasks/",
        json={
            "name": "Task B",
            "description": "desc",
            "deadline": "2030-01-01",
            "user_id": str(outsider.id),
        },
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["user"] is None


async def test_manager_sees_all_team_tasks(
    client, make_team, make_user, make_task, login
):
    team = await make_team()
    manager = await make_user(is_manager=True, team_id=team.id)
    executor = await make_user(team_id=team.id)
    task = await make_task(team_id=team.id, user_id=executor.id)
    headers = login(manager)
    resp = client.get("/tasks/", headers=headers)
    assert resp.status_code == 200
    assert any(t["id"] == str(task.id) for t in resp.json())


async def test_executor_sees_only_own_tasks(
    client, make_team, make_user, make_task, login
):
    team = await make_team()
    executor = await make_user(team_id=team.id)
    own = await make_task(team_id=team.id, user_id=executor.id)
    await make_task(team_id=team.id, user_id=None, name="Foreign")
    headers = login(executor)
    resp = client.get("/tasks/", headers=headers)
    assert resp.status_code == 200
    ids = [t["id"] for t in resp.json()]
    assert str(own.id) in ids
    assert all(t["id"] == str(own.id) for t in resp.json())


async def test_manager_modifies_task(
    client, make_team, make_user, make_task, login
):
    team = await make_team()
    manager = await make_user(is_manager=True, team_id=team.id)
    task = await make_task(team_id=team.id)
    headers = login(manager)
    resp = client.patch(
        f"/tasks/{task.id}",
        json={"name": "Renamed"},
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["name"] == "Renamed"


async def test_task_status_flow_opened_progress_done(
    client, make_team, make_user, make_task, login
):
    team = await make_team()
    executor = await make_user(team_id=team.id)
    task = await make_task(team_id=team.id, user_id=executor.id)
    headers = login(executor)

    resp = client.patch(
        f"/tasks/{task.id}/status", json={"status": "progress"}, headers=headers
    )
    assert resp.json()["status"] == "progress"

    resp = client.patch(
        f"/tasks/{task.id}/status", json={"status": "done"}, headers=headers
    )
    assert resp.json()["status"] == "done"


async def test_delete_task_by_manager(
    client, make_team, make_user, make_task, login
):
    team = await make_team()
    manager = await make_user(is_manager=True, team_id=team.id)
    task = await make_task(team_id=team.id)
    headers = login(manager)
    resp = client.delete(f"/tasks/{task.id}", headers=headers)
    assert resp.status_code == 204

    resp = client.get(f"/tasks/{task.id}", headers=headers)
    assert resp.status_code == 404
