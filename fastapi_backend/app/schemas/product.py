from decimal import Decimal

from pydantic import BaseModel
from pydantic import Field


class ProductCreate(BaseModel):

    name: str = Field(
        min_length=1,
        max_length=200
    )

    description: str | None = None

    category: str = Field(
        min_length=1,
        max_length=100
    )

    price: Decimal = Field(
        gt=0
    )

    stock: int = Field(
        ge=0
    )

    popularity: int = Field(
        default=0,
        ge=0
    )

    images: str | None = None


class ProductUpdate(BaseModel):

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=200
    )

    description: str | None = None

    category: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    price: Decimal | None = Field(
        default=None,
        gt=0
    )

    stock: int | None = Field(
        default=None,
        ge=0
    )

    popularity: int | None = Field(
        default=None,
        ge=0
    )

    images: str | None = None


class ProductResponse(ProductCreate):

    id: int

    model_config = {
        "from_attributes": True
    }