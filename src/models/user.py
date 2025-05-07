from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped

from src.models.base import Base


class User(Base, SQLAlchemyBaseUserTable[int]):
    """
    User model.

    Attributes:
        is_manager (bool): Indicates whether the user is a manager.
            Defaults to False.
    """

    is_manager: Mapped[bool] = False

    @classmethod
    def get_db(cls, session: AsyncSession):
        """
        Gets the user database instance associated with the given session.

        Args:
            session (AsyncSession): The asynchronous SQLAlchemy session to use for database operations.

        Returns:
            SQLAlchemyUserDatabase: An instance of SQLAlchemyUserDatabase
            configured with the provided session and user model.
        """

        return SQLAlchemyUserDatabase(session, cls)
