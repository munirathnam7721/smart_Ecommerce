# from datetime import datetime
# from decimal import Decimal
# from enum import Enum

# from sqlalchemy import DateTime
# from sqlalchemy import Enum as SAEnum
# from sqlalchemy import ForeignKey
# from sqlalchemy import Numeric
# from sqlalchemy import String

# from sqlalchemy.orm import Mapped
# from sqlalchemy.orm import mapped_column

# from app.db.session import Base


# # ============================================================
# # PAYMENT STATUS
# # ============================================================

# class PaymentStatus(
#     str,
#     Enum,
# ):

#     pending = "pending"

#     paid = "paid"

#     failed = "failed"

#     refunded = "refunded"


# # ============================================================
# # PAYMENT
# # ============================================================

# class Payment(
#     Base,
# ):

#     __tablename__ = "payments"


#     id: Mapped[int] = mapped_column(
#         primary_key=True,
#     )


#     order_id: Mapped[int] = mapped_column(

#         ForeignKey(
#             "orders.id",
#             ondelete="CASCADE",
#         ),

#         nullable=False,

#         unique=True,

#         index=True,

#     )


#     amount: Mapped[
#         Decimal
#     ] = mapped_column(

#         Numeric(
#             12,
#             2,
#         ),

#         nullable=False,

#     )


#     payment_method: Mapped[
#         str
#     ] = mapped_column(

#         String(50),

#         nullable=False,

#     )


#     transaction_id: Mapped[
#         str | None
#     ] = mapped_column(

#         String(255),

#         nullable=True,

#         unique=True,

#     )


#     status: Mapped[
#         PaymentStatus
#     ] = mapped_column(

#         SAEnum(
#             PaymentStatus,
#             native_enum=False,
#         ),

#         default=PaymentStatus.pending,

#         nullable=False,

#         index=True,

#     )


#     timestamp: Mapped[
#         datetime
#     ] = mapped_column(

#         DateTime,

#         default=datetime.utcnow,

#         nullable=False,

#     # )


from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy import Boolean

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.session import Base


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
# PAYMENT
# ============================================================

class Payment(
    Base,
):

    __tablename__ = "payments"

    # --------------------------------------------------------
    # ID
    # --------------------------------------------------------

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    # --------------------------------------------------------
    # ORDER ID
    # --------------------------------------------------------

    order_id: Mapped[int] = mapped_column(

        ForeignKey(
            "orders.id",
            ondelete="CASCADE",
        ),

        nullable=False,

        unique=True,

        index=True,
    )

    # --------------------------------------------------------
    # AMOUNT
    # --------------------------------------------------------

    amount: Mapped[
        Decimal
    ] = mapped_column(

        Numeric(
            12,
            2,
        ),

        nullable=False,
    )

    # --------------------------------------------------------
    # PAYMENT METHOD
    # --------------------------------------------------------

    payment_method: Mapped[
        str
    ] = mapped_column(

        String(50),

        nullable=False,
    )

    # --------------------------------------------------------
    # TRANSACTION ID
    # --------------------------------------------------------

    transaction_id: Mapped[
        str | None
    ] = mapped_column(

        String(255),

        nullable=True,

        unique=True,
    )

    # --------------------------------------------------------
    # PAYMENT STATUS
    # --------------------------------------------------------

    status: Mapped[
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
    # EMAIL SENT
    #
    # Prevents duplicate payment-success emails.
    # --------------------------------------------------------

    email_sent: Mapped[
        bool
    ] = mapped_column(

        Boolean,

        default=False,

        nullable=False,

        index=True,
    )

    # --------------------------------------------------------
    # TIMESTAMP
    # --------------------------------------------------------

    timestamp: Mapped[
        datetime
    ] = mapped_column(

        DateTime,

        default=datetime.utcnow,

        nullable=False,
    )