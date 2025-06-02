import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from fastapi import FastAPI

from src.config import settings
from src.models import test_dbh, Base
from src.routers import router

test_db = test_dbh(
    settings.db.test_url,
)


async def override_get_async_session():
    """
    Overrides dependency for getting asynchronous session for testing.

    Yields:
        AsyncSession: Asynchronous session for testing.
    """
    async with test_db.session_factory() as session:
        yield session


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    """
    Yields event loop for test session.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def app() -> AsyncGenerator[LifespanManager, Any]:
    """
    Create FastAPI application for testing.

    Yields:
         FastAPI application.
    """

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """
        Create testing database for tests.
        """
        async with test_db.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        yield
        async with test_db.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    test_app = FastAPI(
        docs_url=None,
        redoc_url=None,
        lifespan=lifespan,
    )
    test_app.include_router(router=router)
    test_app.dependency_overrides[test_db.session_getter] = override_get_async_session

    async with LifespanManager(test_app) as manager:
        yield manager.app


@pytest_asyncio.fixture(scope="function", autouse=True)
async def get_async_session():
    """
    Overrides dependency for getting asynchronous session for testing.

    Yields:
        AsyncSession: Asynchronous session for testing.
    """
    async with test_db.session_factory() as session:
        yield session
