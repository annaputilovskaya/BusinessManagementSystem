from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPBearer
from fastapi_users import FastAPIUsers
from fastapi_users.db import BaseUserDatabase
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.auth_backend import authentication_backend
from src.models.database import dbh
from src.models.user import User
from src.models.user_manager import UserManager


async def get_user_db(
    session: AsyncSession = Depends(dbh.session_getter),
):
    """
    Retrieves the user database session.

    Uses dependency injection to get an asynchronous
    session from the database, then yields the user database instance.

    Args:
        session (AsyncSession): The database session obtained through
           dependency injection.

    Yields:
        UserDB (BaseUserDatabase): An instance of the user database for the current session.

    """
    yield SQLAlchemyUserDatabase(session=session, user_table=User)


async def get_user_manager(user_db: BaseUserDatabase[User, UUID] = Depends(get_user_db)):
    """
    Creates and retrieves a user manager instance.

    Args:
        user_db (BaseUserDatabase): The user in database instance obtained through
        dependency injection.

    Yields:
        UserManager: An instance of UserManager configured with the user in
        database.
    """
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, UUID](
    get_user_manager,
    [authentication_backend],
)

current_active_verified_user = fastapi_users.current_user(active=True, verified=True)
current_active_verified_superuser = fastapi_users.current_user(
    active=True, verified=True, superuser=True
)

http_bearer = HTTPBearer(auto_error=False)
