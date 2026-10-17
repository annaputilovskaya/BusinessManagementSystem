from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from src.models import Base

if TYPE_CHECKING:
    from src.models.user import User


class Team(Base):
    """
    Team model.

    Attributes:
        members (list[User]): The list of team members.
    """

    members: Mapped[list["User"]] = relationship(
        "User", back_populates="team", lazy="selectin"
    )

    def __str__(self):
        """
        Returns the string representation of the team object.
        """
        return f"{self.id}"
