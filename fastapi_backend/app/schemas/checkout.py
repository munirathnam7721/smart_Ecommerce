from decimal import Decimal

from pydantic import BaseModel


class CheckoutResponse(BaseModel):

    order_id: int

    amount: Decimal

    currency: str

    checkout_session_id: str

    checkout_url: str