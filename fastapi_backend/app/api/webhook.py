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
# WEBHOOK
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
    # 2. STRIPE SIGNATURE
    # ========================================================

    stripe_signature = request.headers.get(
        "stripe-signature"
    )

    if not stripe_signature:

        raise HTTPException(
            status_code=400,
            detail="Missing Stripe signature",
        )

    # ========================================================
    # 3. VERIFY WEBHOOK
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
            str(exc),
        )

        raise HTTPException(
            status_code=400,
            detail="Unable to verify Stripe webhook",
        ) from exc

    # ========================================================
    # 4. EVENT INFORMATION
    # ========================================================

    event_type = event.type
    event_id = event.id

    print("=" * 70)
    print("STRIPE WEBHOOK VERIFIED")
    print("Event ID:", event_id)
    print("Event Type:", event_type)
    print("=" * 70)

    # ========================================================
    # 5. ONLY PROCESS CHECKOUT COMPLETED
    # ========================================================

    if event_type != "checkout.session.completed":

        print(
            "Ignoring event:",
            event_type,
        )

        return {
            "status": "ignored",
            "event_type": event_type,
        }

    # ========================================================
    # 6. GET SESSION
    # ========================================================

    session = event.data.object

    session_id = session.id

    stripe_payment_status = getattr(
        session,
        "payment_status",
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

    # ========================================================
    # 7. GET METADATA
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
    # 8. GET ORDER ID
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

    print(
        "Order ID:",
        order_id,
    )

    if not order_id:

        return {
            "status": "ignored",
            "reason": "Order ID missing",
        }

    # ========================================================
    # 9. CONVERT ORDER ID
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
    # 10. FIND ORDER
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
    # 11. FIND PAYMENT
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
    # 12. PAYMENT MUST BE PAID
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
    # 13. UPDATE TRANSACTION ID
    # ========================================================

    if payment.transaction_id != session_id:

        payment.transaction_id = session_id

    # ========================================================
    # 14. CHECK WHETHER ORDER ALREADY PROCESSED
    #
    # This is different from the old code.
    #
    # We DON'T immediately return here.
    #
    # We still check whether the email was sent.
    # ========================================================

    already_paid = (
        order.payment_status
        == PaymentStatus.paid
    )

    if already_paid:

        print(
            f"Order #{order.id} is already PAID."
        )

    # ========================================================
    # 15. PROCESS ORDER ONLY IF NOT ALREADY PAID
    # ========================================================

    if not already_paid:

        user = None

        try:

            print("=" * 70)
            print(
                f"PROCESSING PAYMENT "
                f"FOR ORDER #{order.id}"
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
                    OrderItem.order_id == order.id
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

                    print(
                        "WARNING: Product not found:",
                        order_item.product_id,
                    )

                    continue

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

                product.stock = (
                    product.stock
                    - order_item.quantity
                )

            # ------------------------------------------------
            # REMOVE CART
            # ------------------------------------------------

            cart_items = db.scalars(
                select(Cart).where(
                    Cart.user_id == order.user_id
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
                notification_type="payment_success",
                message=(
                    f"Payment for order "
                    f"#{order.id} was successful."
                ),
            )

            # ------------------------------------------------
            # GET USER
            # ------------------------------------------------

            user = db.get(
                User,
                order.user_id,
            )

            # ------------------------------------------------
            # COMMIT
            # ------------------------------------------------

            db.commit()

            print(
                f"ORDER #{order.id} MARKED PAID"
            )

        except Exception as exc:

            db.rollback()

            print("=" * 70)
            print("WEBHOOK PROCESSING ERROR")
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

    # ========================================================
    # 16. GET USER
    #
    # We do this even if order was already paid.
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

    else:

        print(
            "WARNING: User not found"
        )

    # ========================================================
    # 17. SEND EMAIL
    #
    # This is the important part.
    #
    # Even if verify_payment() marked the order paid,
    # the webhook can still send the email.
    #
    # email_sent prevents duplicate emails.
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
                    f"#{order.id} was successful.\n\n"

                    f"Order Amount: "
                    f"{order.total}\n\n"

                    "Payment Status: Paid\n"
                    "Order Status: Paid\n\n"

                    "Your order has been successfully "
                    "confirmed.\n\n"

                    "Thank you for shopping with "
                    "Smart E-Commerce!\n\n"

                    "Regards,\n"
                    "Smart E-Commerce Team"
                ),
            )

            # ------------------------------------------------
            # ONLY MARK SENT AFTER SUCCESS
            # ------------------------------------------------

            payment.email_sent = True

            db.commit()

            print("=" * 70)
            print("PAYMENT EMAIL SENT SUCCESSFULLY")
            print(
                "email_sent = True"
            )
            print("=" * 70)

        except Exception as exc:

            db.rollback()

            print("=" * 70)
            print("PAYMENT EMAIL FAILED")
            print(
                "ERROR TYPE:",
                type(exc).__name__,
            )
            print(
                "ERROR:",
                str(exc),
            )
            print("=" * 70)

            # Do NOT fail the Stripe payment.
            #
            # The payment is already successful.
            # The email can be retried later.

    elif payment.email_sent:

        print(
            "EMAIL ALREADY SENT - SKIPPING"
        )

    else:

        print(
            "EMAIL NOT SENT: "
            "User/email unavailable."
        )

    # ========================================================
    # 18. FINAL RESPONSE
    # ========================================================

    print("=" * 70)
    print("STRIPE WEBHOOK COMPLETE")
    print("Event ID:", event_id)
    print("Order ID:", order.id)
    print("Payment Status: PAID")
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

        "payment_status": "paid",

        "email_sent":
            payment.email_sent,
    }