from sqladmin import ModelView

from src.models import Comment, Task


class TaskAdmin(ModelView, model=Task):
    """
    Admin view for managing Task instances.
    """

    column_list = [Task.id, Task.name, Task.user_id, Task.status, Task.evaluation]
    column_searchable_list = [Task.status]
    can_create = False
    can_edit = False
    can_delete = False
    form_ajax_refs = {
        "comments": {
            "fields": ("id",),
            "order_by": "id",
        },
    }


class CommentAdmin(ModelView, model=Comment):
    """
    Admin view for managing Comment instances.
    """

    column_list = [Comment.id, Comment.created_at, Comment.user_id, Comment.task_id]
    can_create = False
    can_edit = False
    can_delete = False
