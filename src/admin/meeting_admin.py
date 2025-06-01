from sqladmin import ModelView

from src.models import Meeting


class MeetingAdmin(ModelView, model=Meeting):
    """
    Admin view for managing Meeting instances.
    """
    column_list = [Meeting.id, Meeting.meet_time, Meeting.meet_date, Meeting.is_canceled]
    can_create = False
    can_edit = False
    can_delete = False
