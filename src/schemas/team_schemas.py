from uuid import UUID

from pydantic import BaseModel

from src.schemas.user_schemas import UserRead, UserUpdate


class TeamRead(BaseModel):
    """
    Team read schema.

    Attributes:
        id (UUID): The ID of the team.
        members(list[User]): The list of team employees.
    """

    id: UUID
    members: list[UserRead]
