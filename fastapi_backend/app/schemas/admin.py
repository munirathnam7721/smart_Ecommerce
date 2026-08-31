from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr
from pydantic import Field

from app.models.user import UserRole


# ============================================================
# USER MANAGEMENT
# ============================================================

class AdminUserResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    name: str

    email: EmailStr

    role: UserRole

    is_active: bool

    created_at: datetime


class AdminUserUpdate(BaseModel):

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=120,
    )

    email: EmailStr | None = None


class AdminUserRoleUpdate(BaseModel):

    role: UserRole


class AdminUserStatusUpdate(BaseModel):

    is_active: bool


# ============================================================
# PRODUCT MANAGEMENT
# ============================================================

class AdminProductCreate(BaseModel):

    name: str = Field(
        min_length=1,
        max_length=200,
    )

    description: str | None = None

    category: str = Field(
        min_length=1,
        max_length=100,
    )

    price: Decimal = Field(
        ge=0,
    )

    stock: int = Field(
        ge=0,
    )


class AdminProductUpdate(BaseModel):

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    description: str | None = None

    category: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    price: Decimal | None = Field(
        default=None,
        ge=0,
    )

    stock: int | None = Field(
        default=None,
        ge=0,
    )


# ============================================================
# ORDER MANAGEMENT
# ============================================================

class AdminOrderStatusUpdate(BaseModel):

    order_status: str


# ============================================================
# ANALYTICS
# ============================================================

class RevenuePoint(BaseModel):

    date: str

    revenue: Decimal


class TopProductResponse(BaseModel):

    product_id: int

    product_name: str

    quantity_sold: int

    revenue: Decimal


class LowStockResponse(BaseModel):

    product_id: int

    product_name: str

    stock: int


class AnalyticsResponse(BaseModel):

    total_sales: int

    total_revenue: Decimal

    revenue_trends: list[RevenuePoint]

    top_selling_products: list[TopProductResponse]

    low_stock_products: list[LowStockResponse]