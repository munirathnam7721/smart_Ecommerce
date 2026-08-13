from typing import Sequence
from typing import Union

from alembic import op

import sqlalchemy as sa


revision = "0001_initial"

down_revision = None

branch_labels = None

depends_on = None


def upgrade():

    user_role = sa.Enum(
        "admin",
        "staff",
        "customer",
        name="userrole",
        native_enum=False
    )

    op.create_table(

        "users",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True
        ),

        sa.Column(
            "name",
            sa.String(120),
            nullable=False
        ),

        sa.Column(
            "email",
            sa.String(255),
            nullable=False
        ),

        sa.Column(
            "password_hash",
            sa.String(512),
            nullable=True
        ),

        sa.Column(
            "role",
            user_role,
            nullable=False
        ),

        sa.Column(
            "auth0_sub",
            sa.String(255),
            nullable=True
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False
        )
    )

    op.create_index(
        "ix_users_id",
        "users",
        ["id"]
    )

    op.create_index(
        "ix_users_email",
        "users",
        ["email"],
        unique=True
    )

    op.create_index(
        "ix_users_auth0_sub",
        "users",
        ["auth0_sub"],
        unique=True
    )


    op.create_table(

        "products",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True
        ),

        sa.Column(
            "name",
            sa.String(200),
            nullable=False
        ),

        sa.Column(
            "description",
            sa.Text(),
            nullable=True
        ),

        sa.Column(
            "price",
            sa.Numeric(12, 2),
            nullable=False
        ),

        sa.Column(
            "stock",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "images",
            sa.Text(),
            nullable=True
        )
    )


    op.create_index(
        "ix_products_id",
        "products",
        ["id"]
    )


    op.create_table(

        "carts",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "product_id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "quantity",
            sa.Integer(),
            nullable=False
        ),

        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE"
        ),

        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            ondelete="CASCADE"
        ),

        sa.UniqueConstraint(
            "user_id",
            "product_id",
            name="uq_cart_user_product"
        )
    )


def downgrade():

    op.drop_table("carts")

    op.drop_table("products")

    op.drop_table("users")