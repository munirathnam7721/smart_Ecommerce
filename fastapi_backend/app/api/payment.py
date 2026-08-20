import stripe

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db

from app.models.order import (
    Order,
    OrderStatus,
    PaymentStatus,
)

from app.models.payment import Payment


router = APIRouter(
    prefix="/payment",
    tags=["Payment"],
)


@router.get("/verify")
def verify_payment(
    session_id: str,
    db: Session = Depends(get_db),
):
    """
    Verify a Stripe Checkout Session and update
    the corresponding order/payment.
    """

    # --------------------------------------------------
    # 1. Retrieve Checkout Session from Stripe
    # --------------------------------------------------

    try:
        stripe.api_key = settings.stripe_secret_key

        session = stripe.checkout.Session.retrieve(
            session_id
        )

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail="Unable to verify Stripe payment",
        ) from exc

    # --------------------------------------------------
    # 2. Check payment status
    # --------------------------------------------------

    if session.payment_status != "paid":

        return {
            "success": False,
            "payment_status": session.payment_status,
            "message": "Payment has not been completed",
        }

    # --------------------------------------------------
    # 3. Get order ID from Stripe metadata
    # --------------------------------------------------

    order_id = session.metadata.get(
        "order_id"
    )

    if not order_id:

        raise HTTPException(
            status_code=400,
            detail="Order ID missing from Stripe session",
        )

    order = db.get(
        Order,
        int(order_id)
    )

    if not order:

        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    # --------------------------------------------------
    # 4. Find payment record
    # --------------------------------------------------

    payment = db.scalar(
        select(Payment).where(
            Payment.order_id == order.id
        )
    )

    if not payment:

        raise HTTPException(
            status_code=404,
            detail="Payment record not found",
        )

    # --------------------------------------------------
    # 5. Mark payment as successful
    # --------------------------------------------------

    payment.status = PaymentStatus.paid

    payment.transaction_id = session.id

    order.payment_status = PaymentStatus.paid

    order.order_status = OrderStatus.paid

    db.commit()

    return {
        "success": True,
        "order_id": order.id,
        "payment_status": "paid",
        "order_status": "paid",
        "message": "Payment verified successfully",
    }