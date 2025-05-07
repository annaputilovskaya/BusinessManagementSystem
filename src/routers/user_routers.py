from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from src.auth.auth_backend import authentication_backend
from src.auth.dependencies import fastapi_users
from src.schemas.user_schemas import UserRead, UserCreate, UserUpdate

http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(http_bearer)],
)

# /login
# /logout
router.include_router(
    fastapi_users.get_auth_router(
        authentication_backend,
        requires_verification=True,
    ),
)
# /register
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
)
# /me
# /{id}
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
)
# /request-verify-token
# /verify
router.include_router(
    fastapi_users.get_verify_router(UserRead),
)
# /forgot-password
# /reset-password
router.include_router(fastapi_users.get_reset_password_router())
