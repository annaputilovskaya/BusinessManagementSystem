from pydantic import BaseModel

from src.schemas.user_schemas import UserRead, UserUpdate


class TeamRead(BaseModel):
    """
    Team read schema.

    Attributes:
        id (int): The ID of the team.
        members(list[User]): The list of team employees.
    """

    id: int
    members: list[UserRead]
