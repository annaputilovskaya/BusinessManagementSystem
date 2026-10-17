async def test_evaluate_done_task(client, make_team, make_user, make_task, login):
    team = await make_team()
    manager = await make_user(is_manager=True, team_id=team.id)
    executor = await make_user(team_id=team.id)
    task = await make_task(team_id=team.id, user_id=executor.id, status="done")
    headers = login(manager)
    resp = client.post(f"/evaluations/{task.id}", json={"number": 5}, headers=headers)
    assert resp.status_code == 200, resp.text
    assert resp.json()["number"] == 5


async def test_cannot_evaluate_not_done_task(
    client, make_team, make_user, make_task, login
):
    team = await make_team()
    manager = await make_user(is_manager=True, team_id=team.id)
    task = await make_task(team_id=team.id)
    headers = login(manager)
    resp = client.post(f"/evaluations/{task.id}", json={"number": 3}, headers=headers)
    assert resp.status_code == 404


async def test_duplicate_evaluation_conflict(
    client, make_team, make_user, make_task, login
):
    team = await make_team()
    manager = await make_user(is_manager=True, team_id=team.id)
    task = await make_task(team_id=team.id, status="done")
    headers = login(manager)
    resp = client.post(f"/evaluations/{task.id}", json={"number": 4}, headers=headers)
    assert resp.status_code == 200, resp.text
    resp = client.post(f"/evaluations/{task.id}", json={"number": 2}, headers=headers)
    assert resp.status_code == 409


async def test_average_evaluation(client, make_team, make_user, make_task, login):
    team = await make_team()
    manager = await make_user(is_manager=True, team_id=team.id)
    executor = await make_user(team_id=team.id)
    headers = login(manager)
    for number in (4, 5):
        task = await make_task(team_id=team.id, user_id=executor.id, status="done")
        resp = client.post(
            f"/evaluations/{task.id}", json={"number": number}, headers=headers
        )
        assert resp.status_code == 200, resp.text

    resp = client.get(f"/evaluations/average/{executor.id}", headers=headers)
    assert resp.status_code == 200, resp.text
    assert resp.json() == 4.5


async def test_executor_reads_own_evaluations(
    client, make_team, make_user, make_task, login
):
    team = await make_team()
    manager = await make_user(is_manager=True, team_id=team.id)
    executor = await make_user(team_id=team.id)
    task = await make_task(team_id=team.id, user_id=executor.id, status="done")
    headers = login(manager)
    client.post(f"/evaluations/{task.id}", json={"number": 3}, headers=headers)

    exec_headers = login(executor)
    resp = client.get(f"/evaluations/average/{executor.id}", headers=exec_headers)
    assert resp.status_code == 200
    assert resp.json() == 3.0


async def test_foreign_executor_average_forbidden(client, make_team, make_user, login):
    team = await make_team()
    executor = await make_user(team_id=team.id)
    stranger = await make_user(team_id=team.id)
    headers = login(stranger)
    resp = client.get(f"/evaluations/average/{executor.id}", headers=headers)
    assert resp.status_code == 403


async def test_delete_evaluation_by_manager(
    client, make_team, make_user, make_task, login
):
    team = await make_team()
    manager = await make_user(is_manager=True, team_id=team.id)
    task = await make_task(team_id=team.id, status="done")
    headers = login(manager)
    client.post(f"/evaluations/{task.id}", json={"number": 4}, headers=headers)
    resp = client.delete(f"/evaluations/{task.id}", headers=headers)
    assert resp.status_code == 204
