"""add product category and popularity

Revision ID: 5ba6b1dfebe3
Revises: 0001_initial
Create Date: 2026-08-14

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "5ba6b1dfebe3"

down_revision: Union[str, Sequence[str], None] = "0001_initial"

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.add_column(
        "products",
        sa.Column(
            "category",
            sa.String(length=100),
            nullable=False,
            server_default="General"
        )
    )

    op.add_column(
        "products",
        sa.Column(
            "popularity",
            sa.Integer(),
            nullable=False,
            server_default="0"
        )
    )

    op.create_index(
        "ix_products_category",
        "products",
        ["category"],
        unique=False
    )

    op.create_index(
        "ix_products_popularity",
        "products",
        ["popularity"],
        unique=False
    )


def downgrade() -> None:

    op.drop_index(
        "ix_products_popularity",
        table_name="products"
    )

    op.drop_index(
        "ix_products_category",
        table_name="products"
    )

    op.drop_column(
        "products",
        "popularity"
    )

    op.drop_column(
        "products",
        "category"
    )