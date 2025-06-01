from fastapi import FastAPI
from sqladmin import Admin

from src.admin import admin_models
from src.models import dbh


def setup_admin(app: FastAPI):
    admin = Admin(app=app, engine=dbh.engine)
    for model in admin_models:
        admin.add_view(model)
