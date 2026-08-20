from decimal import Decimal

import stripe

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import status

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
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

from app.schemas.checkout import CheckoutResponse

from app.services.stripe_service import (
    create_checkout_session,
)


router = APIRouter(
    prefix="/checkout",
    tags=["Checkout"]
)


# ============================================================
# CREATE CHECKOUT
# ============================================================

@router.post(
    "",
    response_model=CheckoutResponse,
    status_code=status.HTTP_201_CREATED
)
def checkout(
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # 1. Get user's cart
    # --------------------------------------------------------

    cart_items = db.scalars(
        select(Cart).where(
            Cart.user_id == current_user.id
        )
    ).all()

    if not cart_items:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty"
        )

    # --------------------------------------------------------
    # 2. Validate products and calculate total
    # --------------------------------------------------------

    subtotal = Decimal("0.00")

    validated_items = []

    for cart_item in cart_items:

        product = db.get(
            Product,
            cart_item.product_id
        )

        if not product:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Product {cart_item.product_id} "
                    "no longer exists"
                )
            )

        if product.stock < cart_item.quantity:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Insufficient stock for "
                    f"{product.name}"
                )
            )

        price = Decimal(
            str(product.price)
        )

        item_total = (
            price * cart_item.quantity
        )

        subtotal += item_total

        validated_items.append(
            (
                cart_item,
                product,
                price,
                item_total
            )
        )

    # --------------------------------------------------------
    # 3. Calculate final total
    # --------------------------------------------------------

    total = subtotal.quantize(
        Decimal("0.01")
    )

    # --------------------------------------------------------
    # 4. Create order
    # --------------------------------------------------------

    order = Order(
        user_id=current_user.id,
        total=total,
        payment_status=PaymentStatus.pending,
        order_status=OrderStatus.pending
    )

    db.add(order)

    db.flush()

    # --------------------------------------------------------
    # 5. Create order items
    # --------------------------------------------------------

    for (
        cart_item,
        product,
        price,
        item_total
    ) in validated_items:

        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=cart_item.quantity,
            price=price,
            item_total=item_total
        )

        db.add(order_item)

    # --------------------------------------------------------
    # 6. Create pending payment
    # --------------------------------------------------------

    payment = Payment(
        order_id=order.id,
        amount=total,
        payment_method="stripe",
        status=PaymentStatus.pending
    )

    db.add(payment)

    db.flush()

    # --------------------------------------------------------
    # 7. Create Stripe Checkout Session
    # --------------------------------------------------------

    try:

        session = create_checkout_session(
            order_id=order.id,
            amount=total,
            currency=settings.stripe_currency
        )

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to initialize Stripe payment"
        ) from exc

    # --------------------------------------------------------
    # 8. Save Stripe transaction/session ID
    # --------------------------------------------------------

    payment.transaction_id = session.id

    # --------------------------------------------------------
    # 9. Commit database
    # --------------------------------------------------------

    db.commit()

    # --------------------------------------------------------
    # 10. Return Stripe checkout URL
    # --------------------------------------------------------

    return CheckoutResponse(
        order_id=order.id,
        amount=total,
        currency=settings.stripe_currency,
        checkout_session_id=session.id,
        checkout_url=session.url
    )


# ============================================================
# STRIPE WEBHOOK
# ============================================================

@router.post(
    "/webhook",
    status_code=status.HTTP_200_OK
)
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # 1. Read Stripe request body
    # --------------------------------------------------------

    payload = await request.body()

    stripe_signature = request.headers.get(
        "stripe-signature"
    )

    if not stripe_signature:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe signature"
        )

    # --------------------------------------------------------
    # 2. Verify webhook
    # --------------------------------------------------------

    try:

        event = stripe.Webhook.construct_event(
            payload,
            stripe_signature,
            settings.stripe_webhook_secret
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook payload"
        ) from exc

    except stripe.error.SignatureVerificationError as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Stripe signature"
        ) from exc

    # --------------------------------------------------------
    # 3. Handle successful checkout
    # --------------------------------------------------------

    if event["type"] == "checkout.session.completed":

        session = event["data"]["object"]

        session_id = session.get("id")

        payment_status = session.get(
            "payment_status"
        )

        metadata = session.get(
            "metadata",
            {}
        )

        order_id = metadata.get(
            "order_id"
        )

        # ----------------------------------------------------
        # Make sure we have the order ID
        # ----------------------------------------------------

        if not order_id:

            return {
                "status": "ignored",
                "reason": "Order ID missing"
            }

        # ----------------------------------------------------
        # Find order
        # ----------------------------------------------------

        order = db.get(
            Order,
            int(order_id)
        )

        if not order:

            return {
                "status": "ignored",
                "reason": "Order not found"
            }

        # ----------------------------------------------------
        # Find payment
        # ----------------------------------------------------

        payment = db.scalars(
            select(Payment).where(
                Payment.transaction_id == session_id
            )
        ).first()

        if not payment:

            return {
                "status": "ignored",
                "reason": "Payment not found"
            }

        # ----------------------------------------------------
        # Prevent duplicate processing
        # ----------------------------------------------------

        if order.payment_status == PaymentStatus.paid:

            return {
                "status": "already_processed",
                "order_id": order.id
            }

        # ----------------------------------------------------
        # Confirm Stripe payment
        # ----------------------------------------------------

        if payment_status == "paid":

            # Update payment
            payment.status = PaymentStatus.paid

            # Update order
            order.payment_status = PaymentStatus.paid
            order.order_status = OrderStatus.paid

            # ------------------------------------------------
            # Remove purchased products from cart
            # ------------------------------------------------

            cart_items = db.scalars(
                select(Cart).where(
                    Cart.user_id == order.user_id
                )
            ).all()

            for cart_item in cart_items:

                db.delete(cart_item)

            # ------------------------------------------------
            # Reduce product stock
            # ------------------------------------------------

            order_items = db.scalars(
                select(OrderItem).where(
                    OrderItem.order_id == order.id
                )
            ).all()

            for order_item in order_items:

                product = db.get(
                    Product,
                    order_item.product_id
                )

                if product:

                    product.stock = (
                        product.stock
                        - order_item.quantity
                    )

            # ------------------------------------------------
            # Save changes
            # ------------------------------------------------

            db.commit()

            return {
                "status": "success",
                "order_id": order.id,
                "payment_status": "paid"
            }

        # ----------------------------------------------------
        # Payment was not successful
        # ----------------------------------------------------

        return {
            "status": "pending",
            "order_id": order.id,
            "payment_status": payment_status
        }

    # --------------------------------------------------------
    # Other Stripe events
    # --------------------------------------------------------

    return {
        "status": "ignored",
        "event_type": event["type"]
    }