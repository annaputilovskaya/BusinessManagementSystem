from sqlalchemy import text

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


async def test_alembic_migrations_applied(test_engine):
    async with test_engine.connect() as conn:
        result = await conn.execute(
            text("SELECT version_num FROM alembic_version")
        )
        versions = [row[0] for row in result]
    assert versions, "alembic_version is empty — migrations not applied"
