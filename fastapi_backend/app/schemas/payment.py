from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class PaymentResponse(BaseModel):

    id: int

    order_id: int

    amount: Decimal

    payment_method: str

    transaction_id: str | None = None

    status: str

    timestamp: datetime

    model_config = {
        "from_attributes": True
    }