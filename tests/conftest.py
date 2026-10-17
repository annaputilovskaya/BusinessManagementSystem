import asyncio
import os
import subprocess
import sys
from collections.abc import AsyncGenerator, Callable
from pathlib import Path
from uuid import uuid4

import pytest
import pytest_asyncio
from fastapi_users.password import PasswordHelper
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from starlette.testclient import TestClient

from src.config import settings
from src.main import main_app
from src.models import Base, Task, Team, User, dbh
from src.models.enums import StatusEnum

BASE_DIR = Path(__file__).resolve().parent.parent
password_helper = PasswordHelper()
DEFAULT_PASSWORD = "secret123"


@pytest.fixture(scope="session", autouse=True)
def prepare_test_db() -> None:
    """Create test database (if missing) and apply migrations before tests."""

    admin_url = (
        f"{settings.db.DB_ENGINE}://{settings.db.DB_USER}:{settings.db.DB_PASSWORD}"
        f"@{settings.db.DB_HOST}:{settings.db.DB_PORT}/postgres"
    )
    test_db_name = f"test_{settings.db.DB_NAME}"

    async def create_db() -> None:
        engine = create_async_engine(admin_url, poolclass=NullPool)
        async with engine.connect() as conn:
            await conn.execute(text("COMMIT"))
            try:
                await conn.execute(text(f'CREATE DATABASE "{test_db_name}"'))
            except Exception:  # noqa: BLE001 - database already exists
                pass
        await engine.dispose()

    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(create_db())
    finally:
        loop.close()

    env = {**os.environ, "DATABASE_URL": settings.db.tests_url}
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        env=env,
        cwd=BASE_DIR,
        check=True,
    )


@pytest_asyncio.fixture
async def test_engine():
    engine = create_async_engine(settings.db.tests_url, poolclass=NullPool)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def clean_tables(test_engine) -> AsyncGenerator[None, None]:
    async with test_engine.begin() as conn:
        tables = ", ".join(f'"{t}"' for t in Base.metadata.tables)
        await conn.execute(text(f"TRUNCATE {tables} RESTART IDENTITY CASCADE"))
    yield


@pytest_asyncio.fixture(autouse=True)
async def override_session_dependency(test_engine) -> AsyncGenerator[None, None]:
    factory = async_sessionmaker(test_engine, expire_on_commit=False, autoflush=False)

    async def session_getter() -> AsyncGenerator[AsyncSession, None]:
        async with factory() as session:
            yield session

    main_app.dependency_overrides[dbh.session_getter] = session_getter
    yield
    main_app.dependency_overrides.pop(dbh.session_getter, None)


@pytest.fixture
def client() -> TestClient:
    return TestClient(main_app)


@pytest.fixture
def make_team(test_engine) -> Callable:
    async def _create() -> Team:
        factory = async_sessionmaker(test_engine, expire_on_commit=False)
        async with factory() as session:
            team = Team()
            session.add(team)
            await session.commit()
            await session.refresh(team)
            return team

    return _create


@pytest.fixture
def make_user(test_engine) -> Callable:
    async def _create(
        email: str | None = None,
        password: str = DEFAULT_PASSWORD,
        *,
        is_manager: bool = False,
        is_superuser: bool = False,
        is_verified: bool = True,
        team_id=None,
    ) -> User:
        factory = async_sessionmaker(test_engine, expire_on_commit=False)
        async with factory() as session:
            user = User(
                email=email or f"user-{uuid4().hex[:8]}@test.io",
                hashed_password=password_helper.hash(password),
                is_active=True,
                is_verified=is_verified,
                is_superuser=is_superuser,
                is_manager=is_manager,
                team_id=team_id,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    return _create


@pytest.fixture
def make_task(test_engine) -> Callable:
    async def _create(
        team_id,
        user_id=None,
        *,
        name: str = "Test task",
        deadline=None,
        status: StatusEnum | str = StatusEnum.OPENED,
    ) -> Task:
        from datetime import date

        if isinstance(status, str):
            status = StatusEnum(status)
        factory = async_sessionmaker(test_engine, expire_on_commit=False)
        async with factory() as session:
            task = Task(
                name=name,
                description="Test description",
                deadline=deadline or date.today(),
                team_id=team_id,
                user_id=user_id,
                status=status,
            )
            session.add(task)
            await session.commit()
            await session.refresh(task)
            return task

    return _create


@pytest.fixture
def login(client) -> Callable:
    def _login(user, password: str = DEFAULT_PASSWORD) -> dict[str, str]:
        resp = client.post(
            "/users/login", data={"username": user.email, "password": password}
        )
        assert resp.status_code == 200, resp.text
        return {"Authorization": f"Bearer {resp.json()['access_token']}"}

    return _login
