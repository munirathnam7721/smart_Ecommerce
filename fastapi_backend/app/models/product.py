from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy import Text

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.session import Base


class Product(Base):

    __tablename__ = "products"

    # ============================================================
    # ID
    # ============================================================

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    # ============================================================
    # BASIC PRODUCT INFORMATION
    # ============================================================

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    # ============================================================
    # PRICE
    # ============================================================

    price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    # ============================================================
    # INVENTORY
    # ============================================================

    stock: Mapped[int] = mapped_column(
        nullable=False,
        default=0,
        index=True,
    )

    # ============================================================
    # POPULARITY
    #
    # Used by analytics / top-selling-product logic.
    # ============================================================

    popularity: Mapped[int] = mapped_column(
        nullable=False,
        default=0,
        index=True,
    )

    # ============================================================
    # PRODUCT IMAGES
    #
    # Store image URLs/paths.
    #
    # Example:
    # "/uploads/products/iphone.jpg"
    #
    # Multiple images can be stored as JSON text.
    # ============================================================

    images: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ============================================================
    # ACTIVE / INACTIVE
    #
    # Admin can deactivate a product without permanently
    # deleting it.
    # ============================================================

    is_active: Mapped[bool] = mapped_column(
        nullable=False,
        default=True,
        index=True,
    )

    # ============================================================
    # TIMESTAMPS
    # ============================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )