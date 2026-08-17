from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy import Text

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.session import Base


class Product(Base):

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    price: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    stock: Mapped[int] = mapped_column(
        nullable=False,
        default=0
    )

    popularity: Mapped[int] = mapped_column(
        nullable=False,
        default=0,
        index=True
    )

    images: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )