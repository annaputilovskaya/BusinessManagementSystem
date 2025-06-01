from sqladmin import ModelView

from src.models import Team


class TeamAdmin(ModelView, model=Team):
    """
    Admin view for managing Team instances.
    """
    column_list = [Team.id, Team.members]
