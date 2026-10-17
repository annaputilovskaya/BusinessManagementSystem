from typing import TYPE_CHECKING
from uuid import UUID

from fastapi_users_db_sqlalchemy import (
    SQLAlchemyBaseUserTableUUID,
    SQLAlchemyUserDatabase,
)
from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base, Team

if TYPE_CHECKING:
    from src.models.meeting import Meeting
    from src.models.task import Task


class User(Base, SQLAlchemyBaseUserTableUUID):
    """
    User model.

    Attributes:
        is_manager (bool): Indicates whether the user is a manager.
            Defaults to False.
        team_id (Optional[UUID]): The UUID of the team the user belongs to.
            It can be set to None if the user is not associated with any team.
        team (Team): The team associated with this user, linked via
            a relationship.
        tasks (list[Task]): The list of tasks associated with this user, linked via
            a relationship.
    """

    is_manager: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    team_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("teams.id", ondelete="SET NULL")
    )

    team: Mapped["Team"] = relationship("Team", back_populates="members")
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="user")

    meetings: Mapped[list["Meeting"]] = relationship(
        "Meeting",
        secondary="meeting_user_association",
        back_populates="participants",
    )

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

    def __str__(self):
        """
        Returns the string representation of the user object.
        """
        return f"{self.id}. {self.email} ({self.team_id})"
