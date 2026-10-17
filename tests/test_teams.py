async def test_superuser_creates_team(client, make_user, login):
    admin = await make_user(is_superuser=True)
    headers = login(admin)
    resp = client.post("/teams/", headers=headers)
    assert resp.status_code == 200, resp.text
    assert resp.json()["id"]
    assert resp.json()["members"] == []


async def test_superuser_adds_members_to_team(client, make_team, make_user, login):
    team = await make_team()
    admin = await make_user(is_superuser=True)
    member = await make_user()
    headers = login(admin)
    resp = client.patch(
        f"/teams/{team.id}", json=[str(member.id)], headers=headers
    )
    assert resp.status_code == 200, resp.text

    member_headers = login(member)
    me = client.get("/users/me", headers=member_headers)
    assert me.json()["team_id"] == str(team.id)


async def test_authorized_user_lists_teams(client, make_team, make_user, login):
    team = await make_team()
    user = await make_user()
    headers = login(user)
    resp = client.get("/teams/", headers=headers)
    assert resp.status_code == 200
    assert any(t["id"] == str(team.id) for t in resp.json())


async def test_non_superuser_cannot_add_members(
    client, make_team, make_user, login
):
    team = await make_team()
    user = await make_user()
    other = await make_user()
    headers = login(user)
    resp = client.patch(
        f"/teams/{team.id}", json=[str(other.id)], headers=headers
    )
    assert resp.status_code == 403


async def test_delete_team_by_superuser(client, make_team, make_user, login):
    team = await make_team()
    admin = await make_user(is_superuser=True)
    headers = login(admin)
    resp = client.delete(f"/teams/{team.id}", headers=headers)
    assert resp.status_code == 204
