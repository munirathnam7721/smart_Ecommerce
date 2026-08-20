from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class OrderItemResponse(BaseModel):

    id: int

    product_id: int

    quantity: int

    price: Decimal

    item_total: Decimal

    model_config = {
        "from_attributes": True
    }


class OrderResponse(BaseModel):

    id: int

    user_id: int

    total: Decimal

    payment_status: str

    order_status: str

    created_at: datetime

    items: list[OrderItemResponse] = []

    model_config = {
        "from_attributes": True
    }