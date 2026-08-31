# import stripe

# from fastapi import APIRouter, Depends, HTTPException

# from sqlalchemy import select
# from sqlalchemy.orm import Session

# from app.core.config import settings
# from app.db.session import get_db

# from app.models.order import (
#     Order,
#     OrderStatus,
#     PaymentStatus as OrderPaymentStatus,
# )

# from app.models.payment import (
#     Payment,
#     PaymentStatus as PaymentRecordStatus,
# )


# router = APIRouter(
#     prefix="/payment",
#     tags=["Payment"],
# )


# @router.get("/verify")
# def verify_payment(
#     session_id: str,
#     db: Session = Depends(get_db),
# ):

#     # --------------------------------------------------
#     # 1. Validate session ID
#     # --------------------------------------------------

#     if not session_id:
#         raise HTTPException(
#             status_code=400,
#             detail="Stripe session ID is required",
#         )


#     # --------------------------------------------------
#     # 2. Configure Stripe
#     # --------------------------------------------------

#     stripe.api_key = settings.stripe_secret_key


#     # --------------------------------------------------
#     # 3. Retrieve Stripe Checkout Session
#     # --------------------------------------------------

#     try:

#         checkout_session = stripe.checkout.Session.retrieve(
#             session_id
#         )

#     except stripe.error.StripeError as exc:

#         raise HTTPException(
#             status_code=502,
#             detail="Unable to verify payment with Stripe",
#         ) from exc

#     except Exception as exc:

#         raise HTTPException(
#             status_code=500,
#             detail="Unexpected payment verification error",
#         ) from exc


#     # --------------------------------------------------
#     # DEBUG
#     # --------------------------------------------------

#     print("=" * 60)
#     print("STRIPE PAYMENT VERIFICATION")
#     print("Session ID:", checkout_session.id)
#     print("Payment Status:", checkout_session.payment_status)
#     print("Client Reference ID:", checkout_session.client_reference_id)
#     print("Metadata:", checkout_session.metadata)
#     print("=" * 60)


#     # --------------------------------------------------
#     # 4. Check Stripe payment status
#     # --------------------------------------------------

#     if checkout_session.payment_status != "paid":

#         return {
#             "success": False,
#             "payment_status": checkout_session.payment_status,
#             "message": "Payment has not been completed",
#         }


#     # --------------------------------------------------
#     # 5. Get order ID
#     #
#     # IMPORTANT:
#     # StripeObject does not support .get()
#     # --------------------------------------------------

#     metadata = checkout_session.metadata

#     order_id = None


#     # Try metadata first
#     if metadata:

#         try:

#             metadata_dict = metadata.to_dict()

#             order_id = metadata_dict.get(
#                 "order_id"
#             )

#         except Exception:

#             order_id = None


#     # --------------------------------------------------
#     # Fallback to client_reference_id
#     #
#     # You already set this when creating
#     # the Stripe Checkout Session.
#     # --------------------------------------------------

#     if not order_id:

#         order_id = checkout_session.client_reference_id


#     if not order_id:

#         raise HTTPException(
#             status_code=400,
#             detail=(
#                 "Order ID is missing from "
#                 "Stripe Checkout Session"
#             ),
#         )


#     # --------------------------------------------------
#     # 6. Convert order ID safely
#     # --------------------------------------------------

#     try:

#         order_id = int(order_id)

#     except (ValueError, TypeError) as exc:

#         raise HTTPException(
#             status_code=400,
#             detail="Invalid order ID in Stripe Checkout Session",
#         ) from exc


#     print("ORDER ID FOUND:", order_id)


#     # --------------------------------------------------
#     # 7. Find order
#     # --------------------------------------------------

#     order = db.get(
#         Order,
#         order_id,
#     )


#     if not order:

#         raise HTTPException(
#             status_code=404,
#             detail=f"Order {order_id} not found",
#         )


#     # --------------------------------------------------
#     # 8. Find payment record
#     # --------------------------------------------------

#     payment = db.scalar(

#         select(Payment).where(
#             Payment.order_id == order.id
#         )

#     )


#     if not payment:

#         raise HTTPException(
#             status_code=404,
#             detail=(
#                 f"Payment record for order "
#                 f"{order.id} not found"
#             ),
#         )


#     # --------------------------------------------------
#     # 9. Update payment
#     # --------------------------------------------------

#     try:

#         # ----------------------------------------------
#         # Payment table
#         # ----------------------------------------------

#         payment.status = PaymentRecordStatus.paid

#         payment.transaction_id = (
#             checkout_session.payment_intent
#             or checkout_session.id
#         )


#         # ----------------------------------------------
#         # Orders table
#         # ----------------------------------------------

#         order.payment_status = OrderPaymentStatus.paid

#         order.order_status = OrderStatus.paid


#         # ----------------------------------------------
#         # Save database
#         # ----------------------------------------------

#         db.commit()

#         db.refresh(order)

#         db.refresh(payment)


#         print("=" * 60)
#         print("PAYMENT VERIFIED SUCCESSFULLY")
#         print("Order ID:", order.id)
#         print("Order Payment Status:", order.payment_status)
#         print("Order Status:", order.order_status)
#         print("Transaction ID:", payment.transaction_id)
#         print("=" * 60)


#     except Exception as exc:

#         db.rollback()

#         print("DATABASE UPDATE ERROR:", str(exc))

#         raise HTTPException(
#             status_code=500,
#             detail="Failed to update payment status",
#         ) from exc


#     # --------------------------------------------------
#     # 10. Return success
#     # --------------------------------------------------

#     return {

#         "success": True,

#         "order_id": order.id,

#         "payment_status":
#             order.payment_status.value,

#         "order_status":
#             order.order_status.value,

#         "transaction_id":
#             payment.transaction_id,

#         "message":
#             "Payment verified successfully",

#     }



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


# ============================================================
# VERIFY PAYMENT
# ============================================================

@router.get("/verify")
def verify_payment(
    session_id: str,
    db: Session = Depends(get_db),
):

    # --------------------------------------------------------
    # 1. VALIDATE SESSION ID
    # --------------------------------------------------------

    if not session_id:

        raise HTTPException(
            status_code=400,
            detail="Stripe session ID is required",
        )

    # --------------------------------------------------------
    # 2. STRIPE CONFIGURATION
    # --------------------------------------------------------

    stripe.api_key = settings.stripe_secret_key

    # --------------------------------------------------------
    # 3. GET STRIPE SESSION
    # --------------------------------------------------------

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
            detail="Unable to verify payment with Stripe",
        ) from exc

    except Exception as exc:

        print(
            "Unexpected verification error:",
            str(exc),
        )

        raise HTTPException(
            status_code=500,
            detail="Unexpected payment verification error",
        ) from exc

    # --------------------------------------------------------
    # DEBUG
    # --------------------------------------------------------

    print("=" * 70)
    print("STRIPE PAYMENT VERIFICATION")
    print("Session ID:", checkout_session.id)
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
    print("=" * 70)

    # --------------------------------------------------------
    # 4. CHECK PAYMENT STATUS
    # --------------------------------------------------------

    if checkout_session.payment_status != "paid":

        return {
            "success": False,
            "payment_status":
                checkout_session.payment_status,
            "message":
                "Payment has not been completed",
        }

    # --------------------------------------------------------
    # 5. GET ORDER ID
    # --------------------------------------------------------

    metadata = checkout_session.metadata

    order_id = None

    if metadata:

        try:

            metadata_dict = metadata.to_dict()

            order_id = metadata_dict.get(
                "order_id"
            )

        except Exception:

            order_id = None

    # --------------------------------------------------------
    # FALLBACK
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

    # --------------------------------------------------------
    # 6. CONVERT ORDER ID
    # --------------------------------------------------------

    try:

        order_id = int(order_id)

    except (
        ValueError,
        TypeError,
    ) as exc:

        raise HTTPException(
            status_code=400,
            detail="Invalid order ID in Stripe Checkout Session",
        ) from exc

    print(
        "ORDER ID FOUND:",
        order_id,
    )

    # --------------------------------------------------------
    # 7. FIND ORDER
    # --------------------------------------------------------

    order = db.get(
        Order,
        order_id,
    )

    if not order:

        raise HTTPException(
            status_code=404,
            detail=f"Order {order_id} not found",
        )

    # --------------------------------------------------------
    # 8. FIND PAYMENT
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # 9. UPDATE PAYMENT
    # --------------------------------------------------------

    try:

        payment.status = (
            PaymentRecordStatus.paid
        )

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

        print(
            "DATABASE UPDATE ERROR:",
            str(exc),
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to update payment status",
        ) from exc

    # --------------------------------------------------------
    # 10. SEND EMAIL
    #
    # Only send if email_sent == False.
    # --------------------------------------------------------

    if not payment.email_sent:

        user = db.get(
            User,
            order.user_id,
        )

        if user and user.email:

            customer_name = (
                user.name
                if user.name
                else "Customer"
            )

            try:

                print("=" * 70)
                print("SENDING PAYMENT EMAIL FROM VERIFY")
                print("Order:", order.id)
                print("To:", user.email)
                print("=" * 70)

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

                payment.email_sent = True

                db.commit()

                print(
                    "PAYMENT EMAIL MARKED AS SENT"
                )

            except Exception as exc:

                db.rollback()

                print(
                    "PAYMENT EMAIL FAILED:",
                    str(exc),
                )

                # Important:
                # Payment is already successful.
                # Do not return payment failure.

        else:

            print(
                "EMAIL NOT SENT: "
                "User or email unavailable."
            )

    else:

        print(
            "PAYMENT EMAIL ALREADY SENT - SKIPPING"
        )

    # --------------------------------------------------------
    # 11. REFRESH
    # --------------------------------------------------------

    db.refresh(order)
    db.refresh(payment)

    # --------------------------------------------------------
    # 12. RESPONSE
    # --------------------------------------------------------

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
            "Payment verified successfully",
    }