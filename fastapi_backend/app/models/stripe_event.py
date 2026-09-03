from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.session import Base


# ============================================================
# STRIPE EVENT
# ============================================================

class StripeEvent(Base):

    __tablename__ = "stripe_events"

    # --------------------------------------------------------
    # ID
    # --------------------------------------------------------

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    # --------------------------------------------------------
    # STRIPE EVENT ID
    # --------------------------------------------------------

    event_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    # --------------------------------------------------------
    # EVENT TYPE
    # --------------------------------------------------------

    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # --------------------------------------------------------
    # CREATED AT
    # --------------------------------------------------------

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )