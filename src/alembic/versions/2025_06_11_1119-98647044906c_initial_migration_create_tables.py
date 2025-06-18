"""Initial migration: create tables.

Revision ID: 98647044906c
Revises:
Create Date: 2025-06-11 11:19:16.388646

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "98647044906c"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    sa.Enum("opened", "progress", "done", name="status").create(op.get_bind())
    op.create_table(
        "meetings",
        sa.Column("meet_date", sa.Date(), nullable=False),
        sa.Column("meet_time", sa.Time(), nullable=False),
        sa.Column("is_canceled", sa.Boolean(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_meetings")),
    )
    op.create_index(op.f("ix_meetings_id"), "meetings", ["id"], unique=False)
    op.create_table(
        "teams",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_teams")),
    )
    op.create_index(op.f("ix_teams_id"), "teams", ["id"], unique=False)
    op.create_table(
        "users",
        sa.Column("is_manager", sa.Boolean(), nullable=False),
        sa.Column("team_id", sa.UUID(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("hashed_password", sa.String(length=1024), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["team_id"],
            ["teams.id"],
            name=op.f("fk_users_team_id_teams"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_table(
        "meeting_user_association",
        sa.Column("meeting_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["meeting_id"],
            ["meetings.id"],
            name=op.f("fk_meeting_user_association_meeting_id_meetings"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_meeting_user_association_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "id", name=op.f("pk_meeting_user_association")
        ),
        sa.UniqueConstraint(
            "meeting_id", "user_id", name="idx_unique_meeting_user"
        ),
    )
    op.create_index(
        op.f("ix_meeting_user_association_id"),
        "meeting_user_association",
        ["id"],
        unique=False,
    )
    op.create_table(
        "tasks",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("deadline", sa.Date(), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "opened", "progress", "done", name="status", create_type=False
            ),
            nullable=False,
        ),
        sa.Column("team_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["team_id"],
            ["teams.id"],
            name=op.f("fk_tasks_team_id_teams"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_tasks_user_id_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tasks")),
    )
    op.create_index(op.f("ix_tasks_id"), "tasks", ["id"], unique=False)
    op.create_index(
        op.f("ix_tasks_team_id"), "tasks", ["team_id"], unique=False
    )
    op.create_index(
        op.f("ix_tasks_user_id"), "tasks", ["user_id"], unique=False
    )
    op.create_table(
        "comments",
        sa.Column("text", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("timezone('utc', now())"),
            nullable=False,
        ),
        sa.Column("task_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["task_id"],
            ["tasks.id"],
            name=op.f("fk_comments_task_id_tasks"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_comments_user_id_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_comments")),
    )
    op.create_index(op.f("ix_comments_id"), "comments", ["id"], unique=False)
    op.create_table(
        "evaluations",
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.Date(),
            server_default=sa.text("CURRENT_DATE"),
            nullable=False,
        ),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.CheckConstraint(
            "number >= 1 AND number <= 5",
            name=op.f("ck_evaluations_check_number_range"),
        ),
        sa.ForeignKeyConstraint(
            ["task_id"],
            ["tasks.id"],
            name=op.f("fk_evaluations_task_id_tasks"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_evaluations")),
    )
    op.create_index(
        op.f("ix_evaluations_id"), "evaluations", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_evaluations_task_id"), "evaluations", ["task_id"], unique=True
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_evaluations_task_id"), table_name="evaluations")
    op.drop_index(op.f("ix_evaluations_id"), table_name="evaluations")
    op.drop_table("evaluations")
    op.drop_index(op.f("ix_comments_id"), table_name="comments")
    op.drop_table("comments")
    op.drop_index(op.f("ix_tasks_user_id"), table_name="tasks")
    op.drop_index(op.f("ix_tasks_team_id"), table_name="tasks")
    op.drop_index(op.f("ix_tasks_id"), table_name="tasks")
    op.drop_table("tasks")
    op.drop_index(
        op.f("ix_meeting_user_association_id"),
        table_name="meeting_user_association",
    )
    op.drop_table("meeting_user_association")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_teams_id"), table_name="teams")
    op.drop_table("teams")
    op.drop_index(op.f("ix_meetings_id"), table_name="meetings")
    op.drop_table("meetings")
    sa.Enum("opened", "progress", "done", name="status").drop(op.get_bind())
