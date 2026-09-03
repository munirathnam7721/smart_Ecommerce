import stripe

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import status

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db

from app.models.cart import Cart

from app.models.order import (
    Order,
    OrderStatus,
    PaymentStatus,
)

from app.models.order_item import OrderItem

from app.models.payment import Payment

from app.models.product import Product

from app.models.stripe_event import StripeEvent

from app.models.user import User

from app.services.notification_service import (
    create_notification,
)

from app.services.email_service import (
    send_email,
)


# ============================================================
# STRIPE CONFIGURATION
# ============================================================

stripe.api_key = settings.stripe_secret_key


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/checkout",
    tags=["Stripe Webhook"],
)


# ============================================================
# STRIPE WEBHOOK
# ============================================================

@router.post(
    "/webhook",
    status_code=status.HTTP_200_OK,
)
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db),
):

    print("=" * 70)
    print("STRIPE WEBHOOK STARTED")
    print("=" * 70)

    # ========================================================
    # 1. READ RAW BODY
    # ========================================================

    payload = await request.body()

    print(
        "Webhook payload received:",
        len(payload),
        "bytes",
    )

    # ========================================================
    # 2. GET STRIPE SIGNATURE
    # ========================================================

    stripe_signature = request.headers.get(
        "stripe-signature"
    )

    if not stripe_signature:

        print(
            "ERROR: Stripe signature missing"
        )

        raise HTTPException(
            status_code=400,
            detail="Missing Stripe signature",
        )

    # ========================================================
    # 3. VERIFY STRIPE EVENT
    # ========================================================

    try:

        event = stripe.Webhook.construct_event(

            payload,

            stripe_signature,

            settings.stripe_webhook_secret,
        )

    except ValueError as exc:

        print(
            "INVALID WEBHOOK PAYLOAD:",
            str(exc),
        )

        raise HTTPException(
            status_code=400,
            detail="Invalid webhook payload",
        ) from exc

    except stripe.error.SignatureVerificationError as exc:

        print(
            "INVALID STRIPE SIGNATURE:",
            str(exc),
        )

        raise HTTPException(
            status_code=400,
            detail="Invalid Stripe signature",
        ) from exc

    except Exception as exc:

        print(
            "WEBHOOK VERIFICATION ERROR:",
            type(exc).__name__,
            str(exc),
        )

        raise HTTPException(
            status_code=400,
            detail="Unable to verify Stripe webhook",
        ) from exc

    # ========================================================
    # 4. EVENT INFORMATION
    # ========================================================

    event_id = event.id
    event_type = event.type

    print("=" * 70)
    print("STRIPE WEBHOOK VERIFIED")
    print("Event ID:", event_id)
    print("Event Type:", event_type)
    print("=" * 70)

    # ========================================================
    # 5. IDEMPOTENCY CHECK
    #
    # Stripe can send the same webhook more than once.
    # ========================================================

    existing_event = db.scalar(

        select(StripeEvent).where(
            StripeEvent.event_id == event_id
        )
    )

    if existing_event:

        print("=" * 70)
        print("WEBHOOK ALREADY PROCESSED")
        print("Event ID:", event_id)
        print("=" * 70)

        return {
            "status": "already_processed",
            "event_id": event_id,
        }

    # ========================================================
    # 6. ONLY PROCESS SUPPORTED EVENTS
    # ========================================================

    supported_events = {
        "checkout.session.completed",
        "checkout.session.async_payment_succeeded",
        "checkout.session.async_payment_failed",
    }

    if event_type not in supported_events:

        print(
            "Ignoring unsupported event:",
            event_type,
        )

        # Store event so it won't be processed repeatedly.

        try:

            db.add(
                StripeEvent(
                    event_id=event_id,
                    event_type=event_type,
                )
            )

            db.commit()

        except Exception:

            db.rollback()

        return {
            "status": "ignored",
            "event_type": event_type,
        }

    # ========================================================
    # 7. GET STRIPE SESSION
    # ========================================================

    session = event.data.object

    session_id = session.id

    stripe_payment_status = getattr(
        session,
        "payment_status",
        None,
    )

    stripe_payment_intent = getattr(
        session,
        "payment_intent",
        None,
    )

    print(
        "Stripe Session ID:",
        session_id,
    )

    print(
        "Stripe Payment Status:",
        stripe_payment_status,
    )

    print(
        "Stripe Payment Intent:",
        stripe_payment_intent,
    )

    # ========================================================
    # 8. GET METADATA
    # ========================================================

    raw_metadata = getattr(
        session,
        "metadata",
        None,
    )

    if raw_metadata is None:

        metadata = {}

    elif hasattr(
        raw_metadata,
        "to_dict",
    ):

        metadata = raw_metadata.to_dict()

    elif isinstance(
        raw_metadata,
        dict,
    ):

        metadata = raw_metadata

    else:

        metadata = dict(raw_metadata)

    print(
        "Stripe Metadata:",
        metadata,
    )

    # ========================================================
    # 9. GET ORDER ID
    # ========================================================

    order_id = metadata.get(
        "order_id"
    )

    if not order_id:

        order_id = getattr(
            session,
            "client_reference_id",
            None,
        )

    if not order_id:

        print(
            "Order ID missing"
        )

        return {
            "status": "ignored",
            "reason": "Order ID missing",
        }

    # ========================================================
    # 10. CONVERT ORDER ID
    # ========================================================

    try:

        order_id = int(order_id)

    except (
        TypeError,
        ValueError,
    ):

        return {
            "status": "ignored",
            "reason": "Invalid order ID",
        }

    # ========================================================
    # 11. FIND ORDER
    # ========================================================

    order = db.get(
        Order,
        order_id,
    )

    if not order:

        print(
            f"Order #{order_id} not found"
        )

        return {
            "status": "ignored",
            "reason": "Order not found",
            "order_id": order_id,
        }

    print(
        f"Order #{order.id} found"
    )

    # ========================================================
    # 12. FIND PAYMENT
    # ========================================================

    payment = db.scalar(

        select(Payment).where(
            Payment.order_id == order.id
        )
    )

    if not payment:

        print(
            "Payment record not found"
        )

        return {
            "status": "ignored",
            "reason": "Payment not found",
            "order_id": order.id,
        }

    print(
        f"Payment #{payment.id} found"
    )

    # ========================================================
    # 13. SAVE STRIPE IDs
    # ========================================================

    payment.stripe_session_id = session_id

    if stripe_payment_intent:

        payment.stripe_payment_intent_id = (
            stripe_payment_intent
        )

    # ========================================================
    # 14. ASYNC PAYMENT FAILED
    # ========================================================

    if event_type == (
        "checkout.session.async_payment_failed"
    ):

        payment.status = PaymentStatus.failed

        order.payment_status = (
            PaymentStatus.failed
        )

        order.order_status = (
            OrderStatus.cancelled
        )

        try:

            db.add(
                StripeEvent(
                    event_id=event_id,
                    event_type=event_type,
                )
            )

            db.commit()

        except Exception as exc:

            db.rollback()

            print(
                "Failed payment webhook error:",
                str(exc),
            )

            raise HTTPException(
                status_code=500,
                detail="Webhook processing failed",
            ) from exc

        return {
            "status": "payment_failed",
            "event_id": event_id,
            "order_id": order.id,
        }

    # ========================================================
    # 15. PAYMENT MUST BE PAID
    # ========================================================

    if stripe_payment_status != "paid":

        print(
            "Stripe payment is not paid."
        )

        return {
            "status": "pending",
            "order_id": order.id,
            "payment_status":
                stripe_payment_status,
        }

    # ========================================================
    # 16. PREVENT REFUNDED / RETURNED ORDER FROM
    #     BEING MARKED PAID AGAIN
    # ========================================================

    if (
        order.payment_status
        == PaymentStatus.refunded
        or
        order.order_status
        == OrderStatus.returned
    ):

        print(
            "Order already refunded/returned."
        )

        return {
            "status": "ignored",
            "reason":
                "Order already refunded or returned",
            "order_id": order.id,
        }

    # ========================================================
    # 17. CHECK ALREADY PAID
    # ========================================================

    already_paid = (
        order.payment_status
        == PaymentStatus.paid
    )

    # ========================================================
    # 18. PROCESS PAYMENT
    # ========================================================

    if not already_paid:

        try:

            print("=" * 70)
            print(
                f"PROCESSING PAYMENT FOR ORDER "
                f"#{order.id}"
            )
            print("=" * 70)

            # ------------------------------------------------
            # PAYMENT
            # ------------------------------------------------

            payment.status = (
                PaymentStatus.paid
            )

            # ------------------------------------------------
            # ORDER
            # ------------------------------------------------

            order.payment_status = (
                PaymentStatus.paid
            )

            order.order_status = (
                OrderStatus.paid
            )

            # ------------------------------------------------
            # ORDER ITEMS
            # ------------------------------------------------

            order_items = db.scalars(

                select(OrderItem).where(
                    OrderItem.order_id
                    == order.id
                )
            ).all()

            print(
                "Order items:",
                len(order_items),
            )

            # ------------------------------------------------
            # REDUCE STOCK
            # ------------------------------------------------

            for order_item in order_items:

                product = db.get(
                    Product,
                    order_item.product_id,
                )

                if not product:

                    raise ValueError(
                        f"Product "
                        f"{order_item.product_id} "
                        "not found"
                    )

                print(
                    "Product:",
                    product.name,
                )

                print(
                    "Current stock:",
                    product.stock,
                )

                print(
                    "Quantity:",
                    order_item.quantity,
                )

                if (
                    product.stock
                    < order_item.quantity
                ):

                    raise ValueError(
                        f"Insufficient stock for "
                        f"{product.name}"
                    )

                product.stock -= (
                    order_item.quantity
                )

            # ------------------------------------------------
            # CLEAR CART
            # ------------------------------------------------

            cart_items = db.scalars(

                select(Cart).where(
                    Cart.user_id
                    == order.user_id
                )
            ).all()

            for cart_item in cart_items:

                db.delete(
                    cart_item
                )

            # ------------------------------------------------
            # NOTIFICATION
            # ------------------------------------------------

            create_notification(

                db=db,

                user_id=order.user_id,

                notification_type=(
                    "payment_success"
                ),

                message=(
                    f"Payment for order "
                    f"#{order.id} "
                    "was successful."
                ),
            )

            # ------------------------------------------------
            # RECORD EVENT
            # ------------------------------------------------

            db.add(

                StripeEvent(
                    event_id=event_id,
                    event_type=event_type,
                )
            )

            # ------------------------------------------------
            # COMMIT
            # ------------------------------------------------

            db.commit()

            print("=" * 70)
            print(
                f"ORDER #{order.id} MARKED PAID"
            )
            print("=" * 70)

        except Exception as exc:

            db.rollback()

            print("=" * 70)
            print(
                "WEBHOOK PROCESSING ERROR"
            )
            print(
                "ERROR TYPE:",
                type(exc).__name__,
            )
            print(
                "ERROR:",
                str(exc),
            )
            print("=" * 70)

            raise HTTPException(
                status_code=500,
                detail="Webhook processing failed",
            ) from exc

    else:

        print(
            f"Order #{order.id} already paid."
        )

        # ----------------------------------------------------
        # Record webhook event
        # ----------------------------------------------------

        try:

            db.add(

                StripeEvent(
                    event_id=event_id,
                    event_type=event_type,
                )
            )

            db.commit()

        except Exception:

            db.rollback()

    # ========================================================
    # 19. GET USER
    # ========================================================

    user = db.get(
        User,
        order.user_id,
    )

    if user:

        print(
            "Customer email:",
            user.email,
        )

    # ========================================================
    # 20. SEND PAYMENT SUCCESS EMAIL
    # ========================================================

    if (
        user
        and user.email
        and not payment.email_sent
    ):

        try:

            print("=" * 70)
            print("SENDING PAYMENT SUCCESS EMAIL")
            print("TO:", user.email)
            print("ORDER:", order.id)
            print("=" * 70)

            customer_name = (
                user.name
                if user.name
                else "Customer"
            )

            send_email(

                to_email=user.email,

                subject=(
                    f"Payment Successful - "
                    f"Order #{order.id}"
                ),

                body=(

                    f"Hello {customer_name},\n\n"

                    f"Your payment for order "
                    f"#{order.id} "
                    "was successful.\n\n"

                    f"Order Amount: "
                    f"₹{order.total}\n\n"

                    "Payment Status: Paid\n"

                    "Order Status: Paid\n\n"

                    "Your order has been "
                    "successfully confirmed.\n\n"

                    "Thank you for shopping with "
                    "Smart E-Commerce!\n\n"

                    "Regards,\n"
                    "Smart E-Commerce Team"
                ),
            )

            payment.email_sent = True

            db.commit()

            print(
                "PAYMENT EMAIL SENT SUCCESSFULLY"
            )

        except Exception as exc:

            db.rollback()

            print("=" * 70)
            print(
                "PAYMENT EMAIL FAILED"
            )
            print(
                "ERROR TYPE:",
                type(exc).__name__,
            )
            print(
                "ERROR:",
                str(exc),
            )
            print("=" * 70)

            # Do not fail Stripe webhook
            # because email failed.

    elif payment.email_sent:

        print(
            "EMAIL ALREADY SENT - SKIPPING"
        )

    else:

        print(
            "EMAIL NOT SENT: User/email unavailable."
        )

    # ========================================================
    # 21. FINAL RESPONSE
    # ========================================================

    print("=" * 70)
    print("STRIPE WEBHOOK COMPLETE")
    print("Event ID:", event_id)
    print("Order ID:", order.id)
    print(
        "Payment Status:",
        order.payment_status.value,
    )
    print(
        "Order Status:",
        order.order_status.value,
    )
    print(
        "Email Sent:",
        payment.email_sent,
    )
    print("=" * 70)

    return {

        "status": "success",

        "event_id": event_id,

        "event_type": event_type,

        "order_id": order.id,

        "payment_status":
            order.payment_status.value,

        "order_status":
            order.order_status.value,

        "email_sent":
            payment.email_sent,
    }