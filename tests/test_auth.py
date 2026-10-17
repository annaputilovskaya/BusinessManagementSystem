async def test_register_user(client):
    resp = client.post(
        "/users/register",
        json={"email": "new@test.io", "password": "strongpass1"},
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["email"] == "new@test.io"
    assert body["is_manager"] is False


async def test_login_unverified_user_fails(client, make_user):
    user = await make_user(email="unverified@test.io", is_verified=False)
    resp = client.post(
        "/users/login", data={"username": user.email, "password": "secret123"}
    )
    assert resp.status_code == 400, resp.text


async def test_login_success_returns_bearer_token(client, make_user):
    user = await make_user()
    resp = client.post(
        "/users/login", data={"username": user.email, "password": "secret123"}
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


async def test_login_wrong_password_fails(client, make_user):
    user = await make_user()
    resp = client.post(
        "/users/login", data={"username": user.email, "password": "wrongpass"}
    )
    assert resp.status_code == 400


async def test_current_user_requires_token(client):
    resp = client.get("/users/me")
    assert resp.status_code == 401


async def test_current_user_with_token(client, make_user, login):
    user = await make_user()
    headers = login(user)
    resp = client.get("/users/me", headers=headers)
    assert resp.status_code == 200, resp.text
    assert resp.json()["email"] == user.email
