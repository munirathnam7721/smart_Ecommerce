from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db

from app.models.order import Order
from app.models.order import OrderStatus
from app.models.order import PaymentStatus as OrderPaymentStatus

from app.models.order_item import OrderItem

from app.models.payment import Payment
from app.models.payment import PaymentStatus as PaymentRecordStatus

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
#
# GET /admin/orders
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

                "payment_status": (
                    order.payment_status.value
                    if order.payment_status
                    else None
                ),

                "order_status": (
                    order.order_status.value
                    if order.order_status
                    else None
                ),

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
#
# GET /admin/orders/{order_id}
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

    # --------------------------------------------------------
    # FIND ORDER
    # --------------------------------------------------------

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
    # FIND ORDER ITEMS
    # --------------------------------------------------------

    items = db.scalars(
        select(OrderItem).where(
            OrderItem.order_id == order.id
        )
    ).all()

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {

        "id": order.id,

        "user_id": order.user_id,

        "total": order.total,

        "payment_status": (
            order.payment_status.value
            if order.payment_status
            else None
        ),

        "order_status": (
            order.order_status.value
            if order.order_status
            else None
        ),

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
#
# PATCH /admin/orders/{order_id}/status
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

    # --------------------------------------------------------
    # FIND ORDER
    # --------------------------------------------------------

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
    # VALIDATE ORDER STATUS
    # --------------------------------------------------------

    try:

        new_status = OrderStatus(
            payload.order_status
        )

    except ValueError:

        allowed_statuses = [
            status.value
            for status in OrderStatus
        ]

        raise HTTPException(
            status_code=400,
            detail={
                "message": "Invalid order status",

                "allowed_statuses":
                    allowed_statuses,
            },
        )

    # --------------------------------------------------------
    # OLD STATUS
    # --------------------------------------------------------

    old_status = order.order_status

    # --------------------------------------------------------
    # UPDATE STATUS
    # --------------------------------------------------------

    order.order_status = new_status

    # --------------------------------------------------------
    # NOTIFICATION
    # --------------------------------------------------------

    create_notification(

        db=db,

        user_id=order.user_id,

        notification_type=(
            "order_status_updated"
        ),

        message=(
            f"Order #{order.id} status changed "
            f"from {old_status.value} "
            f"to {new_status.value}."
        ),
    )

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    try:

        db.commit()

        db.refresh(
            order
        )

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to update "
                "order status"
            ),
        ) from exc

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {

        "message":
            "Order status updated",

        "order_id":
            order.id,

        "order_status": (
            order.order_status.value
        ),

        "payment_status": (
            order.payment_status.value
        ),
    }


# ============================================================
# GET PAYMENT STATUS
#
# GET /admin/orders/{order_id}/payment
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

    # --------------------------------------------------------
    # FIND ORDER
    # --------------------------------------------------------

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
    # FIND PAYMENT
    # --------------------------------------------------------

    payment = db.scalar(
        select(Payment).where(
            Payment.order_id == order_id
        )
    )

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {

        "order_id":
            order.id,

        "order_payment_status": (
            order.payment_status.value
            if order.payment_status
            else None
        ),

        "payment_record_status": (
            payment.status.value
            if payment
            else None
        ),

        "transaction_id": (
            payment.transaction_id
            if payment
            else None
        ),
    }


# ============================================================
# MARK PAYMENT AS REFUNDED
#
# PATCH /admin/orders/{order_id}/payment/refunded
#
# IMPORTANT:
#
# This endpoint DOES NOT call Stripe.
#
# It only synchronizes the database after the Stripe
# refund has already been successfully completed.
# ============================================================

@router.patch(
    "/{order_id}/payment/refunded"
)
def mark_payment_refunded(

    order_id: int,

    current_user=Depends(
        require_roles(
            UserRole.admin,
        )
    ),

    db: Session = Depends(get_db),
):

    # ========================================================
    # 1. FIND ORDER
    # ========================================================

    order = db.get(
        Order,
        order_id,
    )

    if not order:

        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    # ========================================================
    # 2. FIND PAYMENT
    # ========================================================

    payment = db.scalar(
        select(Payment).where(
            Payment.order_id == order_id
        )
    )

    if not payment:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Payment not found "
                f"for Order #{order_id}"
            ),
        )

    # ========================================================
    # 3. CHECK IF ALREADY REFUNDED
    # ========================================================

    if (
        payment.status
        == PaymentRecordStatus.refunded
    ):

        # Synchronize Order table as well.

        order.payment_status = (
            OrderPaymentStatus.refunded
        )

        order.order_status = (
            OrderStatus.returned
        )

        try:

            db.commit()

            db.refresh(order)

            db.refresh(payment)

        except Exception as exc:

            db.rollback()

            raise HTTPException(
                status_code=500,
                detail=(
                    "Unable to synchronize "
                    "refunded payment"
                ),
            ) from exc

        return {

            "message":
                "Payment already refunded; "
                "order synchronized",

            "order_id":
                order.id,

            "payment_status": (
                order.payment_status.value
            ),

            "payment_record_status": (
                payment.status.value
            ),

            "order_status": (
                order.order_status.value
            ),
        }

    # ========================================================
    # 4. PAYMENT MUST BE PAID
    # ========================================================

    if (
        payment.status
        != PaymentRecordStatus.paid
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Payment cannot be marked "
                "as refunded because current "
                "payment status is "
                f"{payment.status.value}"
            ),
        )

    # ========================================================
    # 5. UPDATE PAYMENT TABLE
    # ========================================================

    payment.status = (
        PaymentRecordStatus.refunded
    )

    # ========================================================
    # 6. UPDATE ORDER TABLE
    # ========================================================

    order.payment_status = (
        OrderPaymentStatus.refunded
    )

    # ========================================================
    # 7. UPDATE ORDER STATUS
    # ========================================================

    order.order_status = (
        OrderStatus.returned
    )

    # ========================================================
    # 8. CREATE NOTIFICATION
    # ========================================================

    create_notification(

        db=db,

        user_id=order.user_id,

        notification_type=(
            "refund_completed"
        ),

        message=(
            f"Refund for Order #{order.id} "
            f"has been completed successfully."
        ),
    )

    # ========================================================
    # 9. SAVE DATABASE
    # ========================================================

    try:

        db.commit()

        db.refresh(
            order
        )

        db.refresh(
            payment
        )

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to update "
                "payment status"
            ),
        ) from exc

    # ========================================================
    # 10. RESPONSE
    # ========================================================

    return {

        "message":
            "Payment marked as refunded",

        "order_id":
            order.id,

        "payment_status": (
            order.payment_status.value
        ),

        "payment_record_status": (
            payment.status.value
        ),

        "order_status": (
            order.order_status.value
        ),
    }