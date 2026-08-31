
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.db.session import get_db

from app.models.order import Order
from app.models.order_item import OrderItem

from app.schemas.order import (
    OrderItemResponse,
    OrderResponse,
)


router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


# ============================================================
# BUILD ORDER RESPONSE
# ============================================================

def build_order_response(
    order: Order,
    db: Session,
):
    items = db.scalars(
        select(OrderItem).where(
            OrderItem.order_id == order.id
        )
    ).all()

    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        total=order.total,
        payment_status=order.payment_status,
        order_status=order.order_status,
        created_at=order.created_at,
        items=[
            OrderItemResponse(
                id=item.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.price,
                item_total=item.item_total,
            )
            for item in items
        ],
    )


# ============================================================
# GET MY ORDERS
# ============================================================

@router.get(
    "",
    response_model=list[OrderResponse],
)
def get_my_orders(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    orders = db.scalars(
        select(Order)
        .where(
            Order.user_id == current_user.id
        )
        .order_by(
            Order.created_at.desc()
        )
    ).all()

    return [
        build_order_response(
            order,
            db,
        )
        for order in orders
    ]


# ============================================================
# GET MY SINGLE ORDER
# ============================================================

@router.get(
    "/{order_id}",
    response_model=OrderResponse,
)
def get_my_order(
    order_id: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    order = db.scalar(
        select(Order).where(
            Order.id == order_id,
            Order.user_id == current_user.id,
        )
    )

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    return build_order_response(
        order,
        db,
    )

