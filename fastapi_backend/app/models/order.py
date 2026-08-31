from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey
from sqlalchemy import Numeric

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.session import Base


# ============================================================
# ORDER STATUS
# ============================================================

class OrderStatus(
    str,
    Enum,
):

    pending = "pending"

    paid = "paid"

    shipped = "shipped"

    delivered = "delivered"

    cancelled = "cancelled"

    # --------------------------------------------------------
    # RETURN REQUESTED
    # --------------------------------------------------------

    return_requested = "return_requested"


# ============================================================
# PAYMENT STATUS
# ============================================================

class PaymentStatus(
    str,
    Enum,
):

    pending = "pending"

    paid = "paid"

    failed = "failed"

    refunded = "refunded"


# ============================================================
# ORDER
# ============================================================

class Order(
    Base,
):

    __tablename__ = "orders"

    # --------------------------------------------------------
    # ID
    # --------------------------------------------------------

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    # --------------------------------------------------------
    # USER ID
    # --------------------------------------------------------

    user_id: Mapped[int] = mapped_column(

        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),

        nullable=False,

        index=True,
    )

    # --------------------------------------------------------
    # TOTAL
    # --------------------------------------------------------

    total: Mapped[Decimal] = mapped_column(

        Numeric(
            12,
            2,
        ),

        nullable=False,
    )

    # --------------------------------------------------------
    # PAYMENT STATUS
    # --------------------------------------------------------

    payment_status: Mapped[
        PaymentStatus
    ] = mapped_column(

        SAEnum(
            PaymentStatus,
            native_enum=False,
        ),

        default=PaymentStatus.pending,

        nullable=False,

        index=True,
    )

    # --------------------------------------------------------
    # ORDER STATUS
    # --------------------------------------------------------

    order_status: Mapped[
        OrderStatus
    ] = mapped_column(

        SAEnum(
            OrderStatus,
            native_enum=False,
        ),

        default=OrderStatus.pending,

        nullable=False,

        index=True,
    )

    # --------------------------------------------------------
    # CREATED AT
    # --------------------------------------------------------

    created_at: Mapped[
        datetime
    ] = mapped_column(

        DateTime,

        default=datetime.utcnow,

        nullable=False,
    )