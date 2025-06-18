from src.admin.meeting_admin import MeetingAdmin
from src.admin.task_admin import TaskAdmin, CommentAdmin
from src.admin.team_admin import TeamAdmin
from src.admin.user_admin import UserAdmin

admin_models = (
    UserAdmin,
    TeamAdmin,
    TaskAdmin,
    CommentAdmin,
    MeetingAdmin,
)
