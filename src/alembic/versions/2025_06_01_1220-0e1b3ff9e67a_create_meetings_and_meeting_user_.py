"""Create meetings and meeting_user_association tables.

Revision ID: 0e1b3ff9e67a
Revises: 0f95c36f359b
Create Date: 2025-06-01 12:20:08.863804

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0e1b3ff9e67a"
down_revision: Union[str, None] = "0f95c36f359b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "meetings",
        sa.Column("meet_date", sa.Date(), nullable=False),
        sa.Column("meet_time", sa.Time(), nullable=False),
        sa.Column("is_canceled", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_meetings")),
    )
    op.create_table(
        "meeting_user_association",
        sa.Column("meeting_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_meeting_user_association")),
        sa.UniqueConstraint("meeting_id", "user_id", name="idx_unique_meeting_user"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("meeting_user_association")
    op.drop_table("meetings")
