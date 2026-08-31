from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

from app.models.return_request import (
    ReturnRequestStatus,
)


# ============================================================
# CREATE RETURN REQUEST
# ============================================================

class ReturnRequestCreate(
    BaseModel,
):

    reason: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    comment: str | None = Field(
        default=None,
        max_length=2000,
    )


# ============================================================
# RETURN REQUEST RESPONSE
# ============================================================

class ReturnRequestResponse(
    BaseModel,
):

    id: int

    order_id: int

    user_id: int

    reason: str

    comment: str | None

    status: ReturnRequestStatus

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )