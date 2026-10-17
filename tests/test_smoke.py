from src.main import main_app


def test_openapi_available(client):
    resp = client.get("/openapi.json")
    assert resp.status_code == 200


def test_routers_registered(client):
    paths = {route.path for route in main_app.routes}
    expected = {
        "/users/login",
        "/users/register",
        "/tasks/",
        "/tasks/{task_id}",
        "/teams/",
        "/meetings/",
        "/evaluations/{task_id}",
        "/schedule/day",
        "/schedule/month",
        "/docs",
    }
    assert expected.issubset(paths), expected - paths
