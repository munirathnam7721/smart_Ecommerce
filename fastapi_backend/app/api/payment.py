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
    PaymentStatus as OrderPaymentStatus,
)

from app.models.payment import (
    Payment,
    PaymentStatus as PaymentRecordStatus,
)

from app.models.user import User

from app.services.email_service import (
    send_email,
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/payment",
    tags=["Payment"],
)


stripe.api_key = settings.stripe_secret_key


# ============================================================
# SEND PAYMENT SUCCESS EMAIL
# ============================================================

def send_payment_success_email(
    db: Session,
    order: Order,
    payment: Payment,
):
    """
    Send payment-success email only once.

    Returns:
        True  -> email sent successfully
        False -> email could not be sent
    """

    # --------------------------------------------------------
    # Already sent
    # --------------------------------------------------------

    if payment.email_sent:
        print("=" * 70)
        print("PAYMENT EMAIL ALREADY SENT")
        print("Order:", order.id)
        print("=" * 70)

        return True

    # --------------------------------------------------------
    # Get user
    # --------------------------------------------------------

    user = db.get(
        User,
        order.user_id,
    )

    if not user:
        print("=" * 70)
        print("PAYMENT EMAIL FAILED")
        print("User not found")
        print("Order:", order.id)
        print("=" * 70)

        return False

    if not user.email:
        print("=" * 70)
        print("PAYMENT EMAIL FAILED")
        print("User email is empty")
        print("User ID:", user.id)
        print("Order:", order.id)
        print("=" * 70)

        return False

    customer_name = (
        user.name
        if user.name
        else "Customer"
    )

    # --------------------------------------------------------
    # Email
    # --------------------------------------------------------

    subject = (
        f"Payment Successful - "
        f"Order #{order.id}"
    )

    body = (
        f"Hello {customer_name},\n\n"

        f"Your payment for order "
        f"#{order.id} was successful.\n\n"

        f"Order Amount: ₹{order.total}\n\n"

        "Payment Status: Paid\n"
        "Order Status: Paid\n\n"

        "Your order has been successfully "
        "confirmed.\n\n"

        "Thank you for shopping with "
        "Smart E-Commerce!\n\n"

        "Regards,\n"
        "Smart E-Commerce Team"
    )

    # --------------------------------------------------------
    # Send
    # --------------------------------------------------------

    try:

        print("=" * 70)
        print("SENDING PAYMENT SUCCESS EMAIL")
        print("Order:", order.id)
        print("User ID:", user.id)
        print("Customer:", customer_name)
        print("Email:", user.email)
        print("=" * 70)

        send_email(
            to_email=user.email,
            subject=subject,
            body=body,
        )

        # ----------------------------------------------------
        # Mark as sent
        # ----------------------------------------------------

        payment.email_sent = True

        db.commit()

        print("=" * 70)
        print("PAYMENT SUCCESS EMAIL SENT")
        print("Order:", order.id)
        print("Email:", user.email)
        print("email_sent:", payment.email_sent)
        print("=" * 70)

        return True

    except Exception as exc:

        db.rollback()

        print("=" * 70)
        print("PAYMENT SUCCESS EMAIL FAILED")
        print("Order:", order.id)
        print("Email:", user.email)
        print("Error Type:", type(exc).__name__)
        print("Error:", str(exc))
        print("=" * 70)

        return False


# ============================================================
# VERIFY PAYMENT
#
# GET /payment/verify?session_id=...
# ============================================================

@router.get("/verify")
def verify_payment(
    session_id: str,
    db: Session = Depends(get_db),
):

    # ========================================================
    # 1. VALIDATE SESSION
    # ========================================================

    if not session_id:
        raise HTTPException(
            status_code=400,
            detail="Stripe session ID is required",
        )

    # ========================================================
    # 2. GET STRIPE SESSION
    # ========================================================

    stripe.api_key = settings.stripe_secret_key

    try:

        checkout_session = (
            stripe.checkout.Session.retrieve(
                session_id
            )
        )

    except stripe.error.StripeError as exc:

        print(
            "Stripe verification error:",
            str(exc),
        )

        raise HTTPException(
            status_code=502,
            detail=(
                "Unable to verify payment with Stripe"
            ),
        ) from exc

    except Exception as exc:

        print(
            "Unexpected verification error:",
            str(exc),
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unexpected payment verification error"
            ),
        ) from exc

    # ========================================================
    # 3. DEBUG STRIPE
    # ========================================================

    print("=" * 70)
    print("STRIPE PAYMENT VERIFICATION")
    print("Session ID:", checkout_session.id)
    print(
        "Session Status:",
        checkout_session.status,
    )
    print(
        "Payment Status:",
        checkout_session.payment_status,
    )
    print(
        "Client Reference ID:",
        checkout_session.client_reference_id,
    )
    print(
        "Metadata:",
        checkout_session.metadata,
    )
    print(
        "Payment Intent:",
        checkout_session.payment_intent,
    )
    print("=" * 70)

    # ========================================================
    # 4. CHECK PAYMENT
    # ========================================================

    if checkout_session.payment_status != "paid":

        return {
            "success": False,
            "payment_status":
                checkout_session.payment_status,
            "message":
                "Payment has not been completed",
        }

    # ========================================================
    # 5. GET ORDER ID
    # ========================================================

    order_id = None

    metadata = checkout_session.metadata

    if metadata:

        try:

            order_id = metadata.get(
                "order_id"
            )

        except Exception:
            order_id = None

    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    if not order_id:

        order_id = (
            checkout_session.client_reference_id
        )

    if not order_id:

        raise HTTPException(
            status_code=400,
            detail=(
                "Order ID is missing from "
                "Stripe Checkout Session"
            ),
        )

    # ========================================================
    # 6. CONVERT ORDER ID
    # ========================================================

    try:

        order_id = int(order_id)

    except (
        ValueError,
        TypeError,
    ) as exc:

        raise HTTPException(
            status_code=400,
            detail="Invalid order ID",
        ) from exc

    # ========================================================
    # 7. GET ORDER
    # ========================================================

    order = db.get(
        Order,
        order_id,
    )

    if not order:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Order {order_id} not found"
            ),
        )

    # ========================================================
    # 8. GET PAYMENT
    # ========================================================

    payment = db.scalar(
        select(Payment).where(
            Payment.order_id == order.id
        )
    )

    if not payment:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Payment record for order "
                f"{order.id} not found"
            ),
        )

    # ========================================================
    # 9. DO NOT CHANGE REFUNDED / RETURNED ORDER
    # ========================================================

    if (
        order.payment_status
        == OrderPaymentStatus.refunded
        or
        order.order_status
        == OrderStatus.returned
    ):

        return {
            "success": True,
            "order_id": order.id,
            "payment_status":
                order.payment_status.value,
            "order_status":
                order.order_status.value,
            "transaction_id":
                payment.transaction_id,
            "email_sent":
                payment.email_sent,
            "message":
                "Order is already refunded/returned",
        }

    # ========================================================
    # 10. UPDATE PAYMENT
    # ========================================================

    try:

        payment.status = (
            PaymentRecordStatus.paid
        )

        # ----------------------------------------------------
        # IMPORTANT
        # ----------------------------------------------------
        # Store PaymentIntent after payment is completed.
        # This is needed for refunds.
        # ----------------------------------------------------

        payment.transaction_id = (
            checkout_session.payment_intent
            or checkout_session.id
        )

        order.payment_status = (
            OrderPaymentStatus.paid
        )

        order.order_status = (
            OrderStatus.paid
        )

        db.commit()

        db.refresh(order)
        db.refresh(payment)

    except Exception as exc:

        db.rollback()

        print("=" * 70)
        print("DATABASE UPDATE FAILED")
        print("Error:", str(exc))
        print("=" * 70)

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to update payment status"
            ),
        ) from exc

    # ========================================================
    # 11. SEND EMAIL
    # ========================================================

    email_sent = send_payment_success_email(
        db=db,
        order=order,
        payment=payment,
    )

    # ========================================================
    # 12. REFRESH
    # ========================================================

    db.refresh(order)
    db.refresh(payment)

    # ========================================================
    # 13. RESPONSE
    # ========================================================

    return {

        "success": True,

        "order_id":
            order.id,

        "payment_status":
            order.payment_status.value,

        "order_status":
            order.order_status.value,

        "transaction_id":
            payment.transaction_id,

        "email_sent":
            payment.email_sent,

        "message":
            (
                "Payment verified successfully"
                if email_sent
                else
                "Payment verified, but email could not be sent"
            ),
    }