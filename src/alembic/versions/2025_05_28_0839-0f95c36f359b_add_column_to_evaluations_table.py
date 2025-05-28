"""Add column to evaluations table.

Revision ID: 0f95c36f359b
Revises: d0ac98b54568
Create Date: 2025-05-28 08:39:50.339979

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0f95c36f359b"
down_revision: Union[str, None] = "d0ac98b54568"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "evaluations",
        sa.Column(
            "created_at",
            sa.Date(),
            server_default=sa.text("CURRENT_DATE"),
            nullable=False,
        ),
    )
    op.create_index(
        op.f("ix_evaluations_task_id"), "evaluations", ["task_id"], unique=True
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_evaluations_task_id"), table_name="evaluations")
    op.drop_column("evaluations", "created_at")
