from fastapi_users.authentication import (
    AuthenticationBackend,
    JWTStrategy,
    BearerTransport,
)

from src.config import settings

bearer_transport = BearerTransport(tokenUrl="users/login")


def get_jwt_strategy() -> JWTStrategy:
    """
    Creates and returns a JWT strategy for authentication.

    This function initializes a JWTStrategy instance with the specified
    secret, lifetime, algorithm, and public key, which are fetched from
    application settings.

    Returns:
        JWTStrategy: An instance of JWTStrategy configured with the
        application's JWT settings.
    """
    return JWTStrategy(
        secret=settings.auth_jwt.private_key_path.read_text(),
        lifetime_seconds=settings.auth_jwt.lifetime_seconds,
        algorithm=settings.auth_jwt.algorithm,
        public_key=settings.auth_jwt.public_key_path.read_text(),
    )


authentication_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
