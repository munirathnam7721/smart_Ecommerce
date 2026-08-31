"""add order items

Revision ID: 34c50f8227dc

Revises: 24e9c676ab7d

Create Date: 2026-08-27 15:52:32.423669
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "34c50f8227dc"

down_revision: Union[str, Sequence[str], None] = "24e9c676ab7d"

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        "order_items",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "order_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "product_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "quantity",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "price",
            sa.Numeric(12, 2),
            nullable=False,
        ),

        sa.Column(
            "item_total",
            sa.Numeric(12, 2),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(
            ["order_id"],
            ["orders.id"],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            ondelete="RESTRICT",
        ),

        sa.PrimaryKeyConstraint(
            "id",
        ),
    )

    op.create_index(
        "ix_order_items_order_id",
        "order_items",
        ["order_id"],
        unique=False,
    )

    op.create_index(
        "ix_order_items_product_id",
        "order_items",
        ["product_id"],
        unique=False,
    )


def downgrade() -> None:

    op.drop_index(
        "ix_order_items_product_id",
        table_name="order_items",
    )

    op.drop_index(
        "ix_order_items_order_id",
        table_name="order_items",
    )

    op.drop_table(
        "order_items",
    )