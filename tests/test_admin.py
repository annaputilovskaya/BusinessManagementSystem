from src.admin.admin_auth import AdminAuth


class FakeRequest:
    def __init__(self, session: dict) -> None:
        self.session = session


async def test_admin_authenticate_without_token():
    auth = AdminAuth(secret_key="test-secret")
    assert await auth.authenticate(FakeRequest({})) is False


async def test_admin_authenticate_with_garbage_token():
    auth = AdminAuth(secret_key="test-secret")
    request = FakeRequest({"admin-token": "not-a-valid-jwt"})
    assert await auth.authenticate(request) is False
