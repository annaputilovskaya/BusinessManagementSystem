from sqladmin import ModelView

from src.models import User


class UserAdmin(ModelView, model=User):
    """
    Admin view for managing User instances.
    """

    column_list = [User.id, User.email, User.is_manager, User.team_id]
    column_searchable_list = [User.team_id]
    form_columns = [
        User.email,
        User.is_active,
        User.is_verified,
        User.is_superuser,
        User.is_manager,
        User.team_id,
    ]
    can_create = False
    form_ajax_refs = {
        "tasks": {
            "fields": ("id",),
            "order_by": "id",
        },
        "meetings": {
            "fields": ("id",),
            "order_by": "id",
        },
    }
