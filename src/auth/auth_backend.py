from fastapi_users.authentication import (
    AuthenticationBackend,
    JWTStrategy,
    BearerTransport,
)

from src.config import settings

bearer_transport = BearerTransport(tokenUrl="users/login")


def get_jwt_strategy() -> JWTStrategy:
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
