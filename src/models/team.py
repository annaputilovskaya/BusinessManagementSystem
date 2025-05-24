from sqlalchemy.orm import Mapped, relationship

from src.models import Base


class Team(Base):
    """
    Team model.

    Attributes:
        members (list[User]): The list of team members.
    """

    members: Mapped[list["User"]] = relationship("User", back_populates="team", lazy="selectin")
