from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Text

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.session import Base


# ============================================================
# RETURN REQUEST STATUS
# ============================================================

class ReturnRequestStatus(
    str,
    Enum,
):

    pending = "pending"

    approved = "approved"

    rejected = "rejected"


# ============================================================
# RETURN REQUEST
# ============================================================

class ReturnRequest(
    Base,
):

    __tablename__ = "return_requests"

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

        index=True,

        unique=True,
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
    # REASON
    # --------------------------------------------------------

    reason: Mapped[str] = mapped_column(

        String(255),

        nullable=False,
    )

    # --------------------------------------------------------
    # COMMENT
    # --------------------------------------------------------

    comment: Mapped[str | None] = mapped_column(

        Text,

        nullable=True,
    )

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    status: Mapped[
        ReturnRequestStatus
    ] = mapped_column(

        SAEnum(
            ReturnRequestStatus,
            native_enum=False,
        ),

        default=ReturnRequestStatus.pending,

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