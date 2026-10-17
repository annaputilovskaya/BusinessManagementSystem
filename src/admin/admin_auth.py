import contextlib

from fastapi_users.exceptions import UserNotExists
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from src.auth.auth_backend import authentication_backend
from src.auth.dependencies import get_user_db, get_user_manager
from src.models import dbh

get_users_db_context = contextlib.asynccontextmanager(get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


@contextlib.asynccontextmanager
async def get_user_manager_instance():
    """Asynchronously provide a user manager instance using an active database session.

    This async context manager sets up the necessary database session and user database
    context, yielding a user manager instance for use within the context block.

    Yields:
        UserManager: An instance of the user manager, which can manage user-related
        operations.
    """

    async with dbh.session_factory() as session:
        async with get_users_db_context(session) as users_db:
            async with get_user_manager_context(users_db) as user_manager:
                yield user_manager


class AdminAuth(AuthenticationBackend):
    """
    Authentication backend for admin users.
    """

    async def login(self, request: Request) -> bool:
        """
        Authenticate admin user with provided credentials.

        Takes the email and password from the request,
        validates them against the stored user credentials, and updates
        the session with a new token if the authentication is successful.

        Args:
            request (Request): The HTTP request containing the login form data.

        Returns:
            bool: True if the login was successful; otherwise, False.

        Raises:
            UserNotExists: If the user does not exist in the database.
        """

        form = await request.form()
        email, password = form["username"], form["password"]

        # Validate username/password credentials
        async with get_user_manager_instance() as user_manager:
            try:
                user = await user_manager.get_by_email(email)
            except UserNotExists:
                return False

            if not user_manager.password_helper.password_hash.verify(
                password, user.hashed_password
            ):
                return False

            if not user.is_active or not user.is_superuser:
                return False

        # And update session
        strategy = authentication_backend.get_strategy()
        token = await strategy.write_token(user)
        request.session.update({"admin-token": token})
        return True

    async def logout(self, request: Request) -> bool:
        """
        Clear the admin user's session.

        Logs out the admin user by clearing the session data.

        Args:
            request (Request): The HTTP request.

        Returns:
            bool: Always returns True, indicating successful logout.
        """
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        """
        Verify if the admin user is currently authenticated.

        Checks for the presence of an 'admin-token' in the
        session to determine if the admin user is authenticated.

        Args:
            request (Request): The HTTP request.

        Returns:
            bool: True if the admin user is authenticated; otherwise, False.
        """
        token = request.session.get("admin-token")
        if not token:
            return False
        return True
