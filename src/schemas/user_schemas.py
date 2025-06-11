from uuid import UUID

from fastapi_users import schemas
from fastapi_users.schemas import model_dump


class UserRead(schemas.BaseUser[UUID]):
    """
    User read schema.

    Attributes:
        is_manager (bool): Indicates if the user has manager privileges.
        Defaults to False.
        team_id (UUID): The UUID of the team, associated with user.
    """

    is_manager: bool = False
    team_id: UUID | None = None


class UserCreate(schemas.BaseUserCreate):
    """
    User creation schema.

    Attributes:
        is_manager (bool): Indicates if the user being created has
        manager privileges. Defaults to False.
        team_id (UUID): The UUID of the team, associated with user.
    """

    is_manager: bool = False
    team_id: UUID | None = None

    def create_update_dict(self):
        """
        Creates a dictionary for creating user information.

        This method generates a dictionary representation of the user
        instance, suitable for creating user information. It excludes
        unset fields and specific attributes that should not be included
        in the created payload.

        Returns:
            dict: A dictionary containing the user's fields, excluding
            unset values and protected attributes.
        """

        return model_dump(
            self,
            exclude_unset=True,
            exclude={
                "id",
                "is_superuser",
                "is_active",
                "is_verified",
                "oauth_accounts",
                "is_manager",
                "team_id",
            },
        )


class UserUpdate(schemas.BaseUserUpdate):
    """
    User update schema.

    Defines the fields that can be updated for an
    existing user, including whether the user is a manager.

    Attributes:
        is_manager (bool): Indicates if the user should be updated to
        have manager privileges. Defaults to False.
        team_id (UUID): The UUID of the team, associated with user.

    """

    is_manager: bool = False
    team_id: UUID | None = None

    def create_update_dict(self):
        """
        Create a dictionary for updating user information.

        Generates a dictionary representation of the user
        instance, suitable for updating user information. It excludes
        unset fields and specific attributes that should not be included
        in the update payload.

        Returns:
            dict: A dictionary containing the user's fields, excluding
            unset values and protected attributes.
        """
        return model_dump(
            self,
            exclude_unset=True,
            exclude={
                "id",
                "is_superuser",
                "is_active",
                "is_verified",
                "oauth_accounts",
                "is_manager",
                "team_id",
            },
        )
