import stripe

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db

from app.models.order import (
    Order,
    OrderStatus,
    PaymentStatus as OrderPaymentStatus,
)

from app.models.order_item import OrderItem

from app.models.product import Product

from app.models.payment import (
    Payment,
    PaymentStatus,
)

from app.models.return_request import (
    ReturnRequest,
    ReturnRequestStatus,
)

from app.models.user import (
    User,
    UserRole,
)

from app.services.notification_service import (
    create_notification,
)

from app.services.email_service import (
    send_email,
)

from app.core.config import settings


# ============================================================
# STRIPE CONFIGURATION
# ============================================================

stripe.api_key = settings.stripe_secret_key


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/admin/returns",
    tags=["Admin - Returns"],
)


# ============================================================
# GET ALL RETURN REQUESTS
#
# GET /admin/returns
# ============================================================

@router.get("")
def get_all_returns(

    current_user=Depends(
        require_roles(
            UserRole.admin,
            UserRole.staff,
        )
    ),

    db: Session = Depends(get_db),
):

    returns = db.scalars(
        select(ReturnRequest)
        .order_by(
            ReturnRequest.created_at.desc()
        )
    ).all()

    result = []

    for return_request in returns:

        # ----------------------------------------------------
        # GET ORDER
        # ----------------------------------------------------

        order = db.get(
            Order,
            return_request.order_id,
        )

        # ----------------------------------------------------
        # GET PAYMENT
        # ----------------------------------------------------

        payment = db.scalar(
            select(Payment).where(
                Payment.order_id
                == return_request.order_id
            )
        )

        # ----------------------------------------------------
        # RETURN INFORMATION
        # ----------------------------------------------------

        result.append(
            {
                "id":
                    return_request.id,

                "order_id":
                    return_request.order_id,

                "user_id":
                    return_request.user_id,

                "reason":
                    return_request.reason,

                "comment":
                    return_request.comment,

                "status":
                    return_request.status.value,

                "created_at":
                    return_request.created_at,

                "order_status": (
                    order.order_status.value
                    if order
                    else None
                ),

                "order_total": (
                    order.total
                    if order
                    else None
                ),

                "payment_status": (
                    payment.status.value
                    if payment
                    else None
                ),

                "order_payment_status": (
                    order.payment_status.value
                    if order
                    else None
                ),
            }
        )

    return result


# ============================================================
# APPROVE RETURN
#
# POST /admin/returns/{return_id}/approve
#
# WORKFLOW:
#
# pending
#    ↓
# approved
#    ↓
# Stripe refund
#    ↓
# refunded
#
# ALSO:
#
# - Restore stock
# - Order = returned
# - Payment = refunded
# - App notification
# - Email notification
# ============================================================

@router.post(
    "/{return_id}/approve"
)
def approve_return(

    return_id: int,

    current_user=Depends(
        require_roles(
            UserRole.admin,
            UserRole.staff,
        )
    ),

    db: Session = Depends(get_db),
):

    print("=" * 70)
    print("ADMIN RETURN APPROVAL STARTED")
    print("Return ID:", return_id)
    print("=" * 70)

    # ========================================================
    # 1. FIND RETURN REQUEST
    # ========================================================

    return_request = db.get(
        ReturnRequest,
        return_id,
    )

    if not return_request:

        raise HTTPException(
            status_code=404,
            detail="Return request not found",
        )

    print(
        "Return request found:",
        return_request.id,
    )

    # ========================================================
    # 2. CHECK RETURN STATUS
    # ========================================================

    if (
        return_request.status
        != ReturnRequestStatus.pending
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Return request cannot be approved "
                f"because its current status is "
                f"{return_request.status.value}"
            ),
        )

    # ========================================================
    # 3. FIND ORDER
    # ========================================================

    order = db.get(
        Order,
        return_request.order_id,
    )

    if not order:

        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    print(
        "Order found:",
        order.id,
    )

    # ========================================================
    # 4. CHECK ORDER STATUS
    # ========================================================

    if (
        order.order_status
        != OrderStatus.return_requested
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Order is not in return_requested status. "
                f"Current status: "
                f"{order.order_status.value}"
            ),
        )

    # ========================================================
    # 5. FIND PAYMENT
    # ========================================================

    payment = db.scalar(
        select(Payment).where(
            Payment.order_id == order.id
        )
    )

    if not payment:

        raise HTTPException(
            status_code=400,
            detail=(
                "Payment record not found "
                f"for Order #{order.id}"
            ),
        )

    print(
        "Payment found:",
        payment.id,
    )

    # ========================================================
    # 6. CHECK PAYMENT STATUS
    # ========================================================

    if payment.status != PaymentStatus.paid:

        raise HTTPException(
            status_code=400,
            detail=(
                "Order payment cannot be refunded "
                f"because payment status is "
                f"{payment.status.value}"
            ),
        )

    # ========================================================
    # 7. GET STRIPE PAYMENT INTENT ID
    #
    # IMPORTANT:
    #
    # Your Payment model contains:
    #
    # stripe_payment_intent_id
    #
    # It does NOT contain:
    #
    # transaction_id
    # ========================================================

    stripe_payment_intent_id = (
        payment.stripe_payment_intent_id
    )

    print(
        "Stripe Payment Intent ID:",
        stripe_payment_intent_id,
    )

    if not stripe_payment_intent_id:

        raise HTTPException(
            status_code=400,
            detail=(
                "Stripe Payment Intent ID not found "
                f"for Order #{order.id}. "
                "The payment record must contain "
                "stripe_payment_intent_id."
            ),
        )

    # ========================================================
    # 8. GET ORDER ITEMS
    # ========================================================

    items = db.scalars(
        select(OrderItem).where(
            OrderItem.order_id == order.id
        )
    ).all()

    if not items:

        raise HTTPException(
            status_code=400,
            detail="Order has no items",
        )

    print(
        "Order items:",
        len(items),
    )

    # ========================================================
    # 9. GET CUSTOMER
    # ========================================================

    user = db.get(
        User,
        order.user_id,
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail=(
                f"User {order.user_id} not found"
            ),
        )

    print(
        "Customer:",
        getattr(
            user,
            "name",
            "Customer",
        ),
    )

    print(
        "Customer Email:",
        user.email,
    )

    # ========================================================
    # 10. CHECK CUSTOMER EMAIL
    # ========================================================

    if not user.email:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Customer email not found "
                f"for User #{order.user_id}"
            ),
        )

    # ========================================================
    # 11. PROCESS STRIPE REFUND
    # ========================================================

    print("=" * 70)
    print("STARTING STRIPE REFUND")
    print(
        "Payment Intent:",
        stripe_payment_intent_id,
    )
    print("=" * 70)

    try:

        refund = stripe.Refund.create(
            payment_intent=(
                stripe_payment_intent_id
            ),
        )

    except stripe.error.StripeError as exc:

        print("=" * 70)
        print("STRIPE REFUND FAILED")
        print(
            "ERROR:",
            str(exc),
        )
        print("=" * 70)

        raise HTTPException(
            status_code=502,
            detail=(
                "Stripe refund failed: "
                f"{str(exc)}"
            ),
        ) from exc

    # ========================================================
    # 12. VERIFY REFUND
    # ========================================================

    print(
        "Stripe Refund ID:",
        refund.id,
    )

    print(
        "Stripe Refund Status:",
        refund.status,
    )

    if refund.status != "succeeded":

        raise HTTPException(
            status_code=502,
            detail=(
                "Stripe refund was not completed. "
                f"Refund status: {refund.status}"
            ),
        )

    print(
        "STRIPE REFUND SUCCESSFUL"
    )

    # ========================================================
    # 13. RESTORE PRODUCT STOCK
    # ========================================================

    print("=" * 70)
    print("RESTORING PRODUCT STOCK")
    print("=" * 70)

    for item in items:

        product = db.get(
            Product,
            item.product_id,
        )

        if not product:

            db.rollback()

            raise HTTPException(
                status_code=404,
                detail=(
                    f"Product {item.product_id} "
                    "not found"
                ),
            )

        print(
            "Product:",
            product.name,
        )

        print(
            "Old stock:",
            product.stock,
        )

        print(
            "Returned quantity:",
            item.quantity,
        )

        product.stock += item.quantity

        print(
            "New stock:",
            product.stock,
        )

    # ========================================================
    # 14. UPDATE RETURN STATUS
    #
    # pending → refunded
    # ========================================================

    return_request.status = (
        ReturnRequestStatus.refunded
    )

    # ========================================================
    # 15. UPDATE ORDER STATUS
    #
    # return_requested → returned
    # ========================================================

    order.order_status = (
        OrderStatus.returned
    )

    # ========================================================
    # 16. UPDATE PAYMENT STATUS
    #
    # paid → refunded
    # ========================================================

    payment.status = (
        PaymentStatus.refunded
    )

    # ========================================================
    # 17. UPDATE ORDER PAYMENT STATUS
    #
    # paid → refunded
    # ========================================================

    order.payment_status = (
        OrderPaymentStatus.refunded
    )

    # ========================================================
    # 18. CREATE APP NOTIFICATION
    # ========================================================

    try:

        create_notification(

            db=db,

            user_id=order.user_id,

            notification_type="refund_completed",

            message=(
                f"Your return for Order #{order.id} "
                "has been approved and your refund "
                "has been completed."
            ),

        )

        print("=" * 70)
        print("APP NOTIFICATION CREATED")
        print("=" * 70)

    except Exception as exc:

        print("=" * 70)
        print(
            "WARNING: APP NOTIFICATION FAILED"
        )
        print(
            "ERROR:",
            str(exc),
        )
        print("=" * 70)

    # ========================================================
    # 19. SAVE DATABASE
    # ========================================================

    try:

        db.commit()

        db.refresh(
            return_request
        )

        db.refresh(
            order
        )

        db.refresh(
            payment
        )

    except Exception as exc:

        db.rollback()

        print("=" * 70)
        print("DATABASE COMMIT FAILED")
        print(
            "ERROR:",
            str(exc),
        )
        print("=" * 70)

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to complete return "
                "refund workflow"
            ),
        ) from exc

    # ========================================================
    # 20. SEND REFUND EMAIL
    # ========================================================

    email_sent = False

    print("=" * 70)
    print("SENDING REFUND SUCCESS EMAIL")
    print("=" * 70)

    print(
        "Order:",
        order.id,
    )

    print(
        "Customer:",
        getattr(
            user,
            "name",
            "Customer",
        ),
    )

    print(
        "Email:",
        user.email,
    )

    print(
        "Refund ID:",
        refund.id,
    )

    print("=" * 70)

    try:

        customer_name = getattr(
            user,
            "name",
            "Customer",
        )

        # ----------------------------------------------------
        # EMAIL SUBJECT
        # ----------------------------------------------------

        email_subject = (
            f"Refund Completed - Order #{order.id}"
        )

        # ----------------------------------------------------
        # EMAIL BODY
        # ----------------------------------------------------

        email_body = f"""
Hello {customer_name},

Your return request for Order #{order.id} has been approved.

Your refund has been successfully completed.

==================================================
REFUND DETAILS
==================================================

Order ID: #{order.id}

Refund ID: {refund.id}

Refund Status: {refund.status}

Payment Status: Refunded

Order Status: Returned

Refund Amount: ₹{order.total}

==================================================

The refunded amount will be credited back to your
original payment method according to your bank or
payment provider's processing time.

Thank you for shopping with us.

Smart E-Commerce Team
"""

        # ----------------------------------------------------
        # SEND EMAIL
        # ----------------------------------------------------

        send_email(

            to_email=user.email,

            subject=email_subject,

            body=email_body,

        )

        email_sent = True

        print("=" * 70)
        print("REFUND EMAIL SENT SUCCESSFULLY")
        print(
            "TO:",
            user.email,
        )
        print("=" * 70)

    except Exception as exc:

        # ----------------------------------------------------
        # IMPORTANT
        #
        # Refund has already completed.
        #
        # Therefore, do NOT rollback database here.
        # ----------------------------------------------------

        print("=" * 70)
        print("WARNING: REFUND EMAIL FAILED")
        print(
            "TO:",
            user.email,
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

    # ========================================================
    # 21. FINAL LOG
    # ========================================================

    print("=" * 70)
    print("RETURN REFUND WORKFLOW COMPLETED")
    print("=" * 70)

    print(
        "Return ID:",
        return_request.id,
    )

    print(
        "Order ID:",
        order.id,
    )

    print(
        "Refund ID:",
        refund.id,
    )

    print(
        "Return Status:",
        return_request.status.value,
    )

    print(
        "Order Status:",
        order.order_status.value,
    )

    print(
        "Payment Status:",
        payment.status.value,
    )

    print(
        "Order Payment Status:",
        order.payment_status.value,
    )

    print(
        "Email Sent:",
        email_sent,
    )

    print("=" * 70)

    # ========================================================
    # 22. SUCCESS RESPONSE
    # ========================================================

    return {

        "message":
            "Return approved and refund completed",

        "return_id":
            return_request.id,

        "order_id":
            order.id,

        "return_status":
            return_request.status.value,

        "order_status":
            order.order_status.value,

        "order_payment_status":
            order.payment_status.value,

        "payment_status":
            payment.status.value,

        "refund_id":
            refund.id,

        "refund_status":
            refund.status,

        "email_sent":
            email_sent,
    }


# ============================================================
# REJECT RETURN
#
# POST /admin/returns/{return_id}/reject
# ============================================================

@router.post(
    "/{return_id}/reject"
)
def reject_return(

    return_id: int,

    current_user=Depends(
        require_roles(
            UserRole.admin,
            UserRole.staff,
        )
    ),

    db: Session = Depends(get_db),
):

    print("=" * 70)
    print("ADMIN RETURN REJECTION STARTED")
    print("Return ID:", return_id)
    print("=" * 70)

    # ========================================================
    # 1. FIND RETURN REQUEST
    # ========================================================

    return_request = db.get(
        ReturnRequest,
        return_id,
    )

    if not return_request:

        raise HTTPException(
            status_code=404,
            detail="Return request not found",
        )

    # ========================================================
    # 2. CHECK RETURN STATUS
    # ========================================================

    if (
        return_request.status
        != ReturnRequestStatus.pending
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Return request cannot be rejected "
                f"because its current status is "
                f"{return_request.status.value}"
            ),
        )

    # ========================================================
    # 3. FIND ORDER
    # ========================================================

    order = db.get(
        Order,
        return_request.order_id,
    )

    if not order:

        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    # ========================================================
    # 4. REJECT RETURN
    # ========================================================

    return_request.status = (
        ReturnRequestStatus.rejected
    )

    # ========================================================
    # 5. RESTORE ORDER STATUS
    #
    # return_requested → delivered
    # ========================================================

    order.order_status = (
        OrderStatus.delivered
    )

    # ========================================================
    # 6. CREATE APP NOTIFICATION
    # ========================================================

    try:

        create_notification(

            db=db,

            user_id=order.user_id,

            notification_type="return_rejected",

            message=(
                f"Your return request for "
                f"Order #{order.id} "
                "has been rejected."
            ),

        )

        print(
            "APP NOTIFICATION CREATED"
        )

    except Exception as exc:

        print(
            "WARNING: Notification creation failed:",
            str(exc),
        )

    # ========================================================
    # 7. SAVE DATABASE
    # ========================================================

    try:

        db.commit()

        db.refresh(
            return_request
        )

        db.refresh(
            order
        )

    except Exception as exc:

        db.rollback()

        print(
            "DATABASE COMMIT FAILED:",
            str(exc),
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to reject return request"
            ),
        ) from exc

    # ========================================================
    # 8. SUCCESS LOG
    # ========================================================

    print("=" * 70)
    print("RETURN REQUEST REJECTED")
    print(
        "Return ID:",
        return_request.id,
    )
    print(
        "Order ID:",
        order.id,
    )
    print("=" * 70)

    # ========================================================
    # 9. SUCCESS RESPONSE
    # ========================================================

    return {

        "message":
            "Return request rejected",

        "return_id":
            return_request.id,

        "order_id":
            order.id,

        "return_status":
            return_request.status.value,

        "order_status":
            order.order_status.value,

        "payment_status":
            order.payment_status.value,
    }