from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.models import Base, Team


class User(Base, SQLAlchemyBaseUserTable[int]):
    """
    User model.

    Attributes:
        is_manager (bool): Indicates whether the user is a manager.
            Defaults to False.
        team_id (Optional[int]): The ID of the team the user belongs to.
            It can be set to None if the user is not associated with any team.
        team (Team): The team associated with this user, linked via
            a relationship.
        tasks (list[Task]): The list of tasks associated with this user, linked via
            a relationship.
    """

    is_manager: Mapped[bool] = mapped_column(
            Boolean, default=False, nullable=False
        )
    team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id", ondelete="SET NULL"))

    team: Mapped["Team"] = relationship("Team", back_populates="members")
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="executor")

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
        return f'{self.id}. {self.email} ({self.team_id})'