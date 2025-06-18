from fastapi import FastAPI
from sqladmin import Admin

from src.admin import admin_models
from src.admin.admin_auth import AdminAuth
from src.config import settings
from src.models import dbh


def setup_admin(app: FastAPI):
    auth_backend = AdminAuth(secret_key=settings.auth_jwt.verification_token_secret)
    admin = Admin(app=app, engine=dbh.engine, authentication_backend=auth_backend)
    for model in admin_models:
        admin.add_view(model)
