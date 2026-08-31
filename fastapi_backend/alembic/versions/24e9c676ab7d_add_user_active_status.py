"""add user active status

Revision ID: 24e9c676ab7d
Revises: 288bed5639c9
Create Date: 2026-08-27 15:24:49.019302

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "24e9c676ab7d"

down_revision: Union[str, Sequence[str], None] = "288bed5639c9"

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.add_column(
        "users",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )

    op.alter_column(
        "users",
        "is_active",
        server_default=None,
    )


def downgrade() -> None:

    op.drop_column(
        "users",
        "is_active",
    )