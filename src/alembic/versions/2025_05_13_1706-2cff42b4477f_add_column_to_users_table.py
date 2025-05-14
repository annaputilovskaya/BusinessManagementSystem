"""Add column to Users table

Revision ID: 2cff42b4477f
Revises: ceed27addf80
Create Date: 2025-05-13 17:06:18.280564

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2cff42b4477f"
down_revision: Union[str, None] = "ceed27addf80"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("users", sa.Column("team_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        None, "users", "teams", ["team_id"], ["id"], ondelete="SET NULL"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(None, "users", type_="foreignkey")
    op.drop_column("users", "team_id")
