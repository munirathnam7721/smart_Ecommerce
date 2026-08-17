from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.session import Base


class Cart(Base):

    __tablename__ = "carts"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "product_id",
            name="uq_cart_user_product"
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey(
            "products.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    quantity: Mapped[int] = mapped_column(
        nullable=False,
        default=1
    )