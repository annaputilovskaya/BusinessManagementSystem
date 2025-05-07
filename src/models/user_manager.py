import logging

from fastapi import Request
from fastapi_users import IntegerIDMixin, BaseUserManager
from fastapi_users.jwt import SecretType

from src.config import settings
from src.models.user import User

log = logging.getLogger(__name__)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    """
    Manages user-related operations such as registration, password reset, and verification.

    Attributes:
        reset_password_token_secret (SecretType): Secret used for generating reset password tokens.
        verification_token_secret (SecretType): Secret used for generating verification tokens.
    """

    reset_password_token_secret: SecretType = (
        settings.auth_jwt.reset_password_token_secret
    )
    verification_token_secret: SecretType = settings.auth_jwt.verification_token_secret

    async def on_after_register(
        self,
        user: User,
        request: Request | None = None,
    ):
        """
        Handles actions to perform after a user registers.

        Args:
            user (User): The user instance that has just registered.
            request (Request | None): The request object, if available.
        """
        log.warning(
            "User %s has registered.",
            user.id,
        )

    async def on_after_forgot_password(
        self,
        user: User,
        token: str,
        request: Request | None = None,
    ):
        """
        Handles actions to perform after a user requests a password reset.

        Args:
            user (User): The user instance that forgot their password.
            token (str): The password reset token generated for the user.
            request (Request | None): The request object, if available.
        """

        log.warning(
            "User %s has forgot their password. Reset token: %s",
            user.id,
            token,
        )

    async def on_after_request_verify(
        self,
        user: User,
        token: str,
        request: Request | None = None,
    ):
        """
        Handles actions to perform after a user requests verification.

        Args:
            user (User): The user instance that requested verification.
            token (str): The verification token generated for the user.
            request (Request | None): The request object, if available.
        """
        log.warning(
            "Verification requested for user %s. Verification token: %s",
            user.id,
            token,
        )
