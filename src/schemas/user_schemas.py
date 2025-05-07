from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    """
    User read schema.

    Attributes:
        is_manager (bool): Indicates if the user has manager privileges.
        Defaults to False.
    """

    is_manager: bool = False


class UserCreate(schemas.BaseUserCreate):
    """
    User creation schema.

    Attributes:
        is_manager (bool): Indicates if the user being created has
        manager privileges. Defaults to False.
    """

    is_manager: bool = False


class UserUpdate(schemas.BaseUserUpdate):
    """
    User update schema.

    Defines the fields that can be updated for an
    existing user, including whether the user is a manager.

    Attributes:
        is_manager (bool): Indicates if the user should be updated to
        have manager privileges. Defaults to False.
    """
    is_manager: bool = False
