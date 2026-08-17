from decimal import Decimal

from pydantic import BaseModel
from pydantic import Field


class CartCreate(BaseModel):

    product_id: int = Field(
        gt=0
    )

    quantity: int = Field(
        gt=0
    )


class CartUpdate(BaseModel):

    quantity: int = Field(
        gt=0
    )


class CartItemResponse(BaseModel):

    id: int

    user_id: int

    product_id: int

    product_name: str

    price: Decimal

    quantity: int

    item_total: Decimal


class CartResponse(BaseModel):

    items: list[CartItemResponse]

    subtotal: Decimal

    tax: Decimal

    grand_total: Decimal