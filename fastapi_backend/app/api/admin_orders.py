from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db

from app.models.order import Order
from app.models.order import OrderStatus

from app.models.order_item import OrderItem

from app.models.user import UserRole

from app.schemas.admin import (
    AdminOrderStatusUpdate,
)

from app.services.notification_service import (
    create_notification,
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/admin/orders",
    tags=["Admin - Orders"],
)


# ============================================================
# GET ALL ORDERS
# ============================================================

@router.get("")
def get_all_orders(
    current_user=Depends(
        require_roles(
            UserRole.admin,
            UserRole.staff,
        )
    ),
    db: Session = Depends(get_db),
):

    orders = db.scalars(
        select(Order)
        .order_by(
            Order.created_at.desc()
        )
    ).all()

    result = []

    for order in orders:

        items = db.scalars(
            select(OrderItem).where(
                OrderItem.order_id == order.id
            )
        ).all()

        result.append(
            {
                "id": order.id,
                "user_id": order.user_id,
                "total": order.total,
                "payment_status": order.payment_status,
                "order_status": order.order_status,
                "created_at": order.created_at,
                "items": [
                    {
                        "id": item.id,
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                        "price": item.price,
                        "item_total": item.item_total,
                    }
                    for item in items
                ],
            }
        )

    return result


# ============================================================
# GET SINGLE ORDER
# ============================================================

@router.get(
    "/{order_id}"
)
def get_order(
    order_id: int,
    current_user=Depends(
        require_roles(
            UserRole.admin,
            UserRole.staff,
        )
    ),
    db: Session = Depends(get_db),
):

    order = db.get(
        Order,
        order_id,
    )

    if not order:

        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    items = db.scalars(
        select(OrderItem).where(
            OrderItem.order_id == order.id
        )
    ).all()

    return {
        "id": order.id,
        "user_id": order.user_id,
        "total": order.total,
        "payment_status": order.payment_status,
        "order_status": order.order_status,
        "created_at": order.created_at,
        "items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price": item.price,
                "item_total": item.item_total,
            }
            for item in items
        ],
    }


# ============================================================
# UPDATE ORDER STATUS
# ============================================================

@router.patch(
    "/{order_id}/status"
)
def update_order_status(
    order_id: int,
    payload: AdminOrderStatusUpdate,
    current_user=Depends(
        require_roles(
            UserRole.admin,
            UserRole.staff,
        )
    ),
    db: Session = Depends(get_db),
):

    order = db.get(
        Order,
        order_id,
    )

    if not order:

        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    # --------------------------------------------------------
    # Validate order status
    # --------------------------------------------------------

    try:

        new_status = OrderStatus(
            payload.order_status
        )

    except ValueError:

        allowed = [
            value.value
            for value in OrderStatus
        ]

        raise HTTPException(
            status_code=400,
            detail={
                "message": "Invalid order status",
                "allowed_statuses": allowed,
            },
        )

    old_status = order.order_status

    order.order_status = new_status

    # --------------------------------------------------------
    # Create database notification
    # --------------------------------------------------------

    create_notification(
        db=db,
        user_id=order.user_id,
        notification_type="order_status_updated",
        message=(
            f"Order #{order.id} status changed "
            f"from {old_status.value} "
            f"to {new_status.value}."
        ),
    )

    db.commit()

    db.refresh(order)

    return {
        "message": "Order status updated",
        "order_id": order.id,
        "order_status": order.order_status,
        "payment_status": order.payment_status,
    }


# ============================================================
# PAYMENT STATUS
# ============================================================

@router.get(
    "/{order_id}/payment"
)
def get_payment_status(
    order_id: int,
    current_user=Depends(
        require_roles(
            UserRole.admin,
            UserRole.staff,
        )
    ),
    db: Session = Depends(get_db),
):

    order = db.get(
        Order,
        order_id,
    )

    if not order:

        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    return {
        "order_id": order.id,
        "payment_status": order.payment_status,
    }