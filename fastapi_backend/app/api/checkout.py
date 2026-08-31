from decimal import Decimal

import stripe

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from sqlalchemy import delete
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

from app.services.notification_service import (
    create_notification,
)

from app.services.stripe_service import (
    create_checkout_session,
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
    tags=["Checkout"],
)


# ============================================================
# CREATE CHECKOUT
#
# POST /checkout
# ============================================================

@router.post(
    "",
    response_model=CheckoutResponse,
    status_code=status.HTTP_201_CREATED,
)
def checkout(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    print("=" * 70)
    print("CHECKOUT STARTED")
    print("User ID:", current_user.id)
    print("=" * 70)

    # ========================================================
    # 1. GET CART
    # ========================================================

    cart_items = db.scalars(
        select(Cart).where(
            Cart.user_id == current_user.id
        )
    ).all()

    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty",
        )

    print("Cart items:", len(cart_items))

    # ========================================================
    # 2. CHECK EXISTING PENDING ORDER
    # ========================================================

    existing_order = db.scalar(
        select(Order)
        .where(
            Order.user_id == current_user.id,
            Order.payment_status == PaymentStatus.pending,
            Order.order_status == OrderStatus.pending,
        )
        .order_by(
            Order.created_at.desc()
        )
    )

    if existing_order:

        print(
            f"Existing pending order found: "
            f"#{existing_order.id}"
        )

        existing_payment = db.scalar(
            select(Payment).where(
                Payment.order_id == existing_order.id
            )
        )

        # ====================================================
        # REUSE EXISTING STRIPE SESSION
        # ====================================================

        if (
            existing_payment
            and existing_payment.transaction_id
        ):
            try:

                existing_session = (
                    stripe.checkout.Session.retrieve(
                        existing_payment.transaction_id
                    )
                )

                if existing_session.status == "open":

                    print(
                        "Reusing Stripe session:",
                        existing_session.id,
                    )

                    return CheckoutResponse(
                        order_id=existing_order.id,
                        amount=existing_order.total,
                        currency=settings.stripe_currency,
                        checkout_session_id=existing_session.id,
                        checkout_url=existing_session.url,
                    )

            except Exception as exc:

                print(
                    "Could not reuse Stripe session:"
                )

                print(
                    type(exc).__name__,
                    str(exc),
                )

        # ====================================================
        # REMOVE OLD PENDING ORDER
        # ====================================================

        try:

            db.execute(
                delete(OrderItem).where(
                    OrderItem.order_id == existing_order.id
                )
            )

            db.execute(
                delete(Payment).where(
                    Payment.order_id == existing_order.id
                )
            )

            db.delete(existing_order)

            db.flush()

            print(
                f"Old pending order "
                f"#{existing_order.id} removed."
            )

        except Exception as exc:

            db.rollback()

            print(
                "ERROR removing old pending order:",
                type(exc).__name__,
                str(exc),
            )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to reset pending checkout",
            ) from exc

    # ========================================================
    # 3. VALIDATE PRODUCTS
    # ========================================================

    subtotal = Decimal("0.00")

    validated_items = []

    for cart_item in cart_items:

        product = db.get(
            Product,
            cart_item.product_id,
        )

        if not product:

            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Product "
                    f"{cart_item.product_id} "
                    "no longer exists"
                ),
            )

        # ----------------------------------------------------
        # Quantity
        # ----------------------------------------------------

        if cart_item.quantity <= 0:

            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Invalid quantity for "
                    f"{product.name}"
                ),
            )

        # ----------------------------------------------------
        # Stock
        # ----------------------------------------------------

        if product.stock < cart_item.quantity:

            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Insufficient stock for "
                    f"{product.name}. "
                    f"Available: {product.stock}"
                ),
            )

        # ----------------------------------------------------
        # Price
        # ----------------------------------------------------

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
                item_total,
            )
        )

    # ========================================================
    # 4. CALCULATE TOTAL
    # ========================================================

    total = subtotal.quantize(
        Decimal("0.01")
    )

    print("Subtotal:", subtotal)
    print("Total:", total)

    # ========================================================
    # 5. CREATE ORDER
    # ========================================================

    order = Order(
        user_id=current_user.id,
        total=total,
        payment_status=PaymentStatus.pending,
        order_status=OrderStatus.pending,
    )

    db.add(order)

    db.flush()

    print(
        f"Created order #{order.id}"
    )

    # ========================================================
    # 6. CREATE ORDER ITEMS
    # ========================================================

    for (
        cart_item,
        product,
        price,
        item_total,
    ) in validated_items:

        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=cart_item.quantity,
            price=price,
            item_total=item_total,
        )

        db.add(order_item)

    # ========================================================
    # 7. CREATE PAYMENT
    # ========================================================

    payment = Payment(
        order_id=order.id,
        amount=total,
        payment_method="stripe",
        status=PaymentStatus.pending,
    )

    db.add(payment)

    db.flush()

    # ========================================================
    # 8. CREATE ORDER NOTIFICATION
    # ========================================================

    create_notification(
        db=db,
        user_id=current_user.id,
        notification_type="order_created",
        message=(
            f"Your order #{order.id} has been "
            "placed and is awaiting payment."
        ),
    )

    # ========================================================
    # 9. CREATE STRIPE CHECKOUT SESSION
    # ========================================================

    try:

        session = create_checkout_session(
            order_id=order.id,
            amount=total,
            currency=settings.stripe_currency,
        )

    except Exception as exc:

        db.rollback()

        print("=" * 70)
        print("STRIPE CHECKOUT CREATION FAILED")
        print("Exception:", type(exc).__name__)
        print("Message:", str(exc))
        print("=" * 70)

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to initialize Stripe payment",
        ) from exc

    # ========================================================
    # 10. SAVE STRIPE SESSION ID
    # ========================================================

    payment.transaction_id = session.id

    print(
        "Stripe Session ID:",
        session.id,
    )

    # ========================================================
    # 11. COMMIT
    # ========================================================

    try:

        db.commit()

    except Exception as exc:

        db.rollback()

        print(
            "DATABASE COMMIT FAILED:",
            type(exc).__name__,
            str(exc),
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save checkout",
        ) from exc

    print(
        f"Order #{order.id} committed successfully"
    )

    # ========================================================
    # 12. RETURN CHECKOUT
    # ========================================================

    print("=" * 70)
    print("CHECKOUT CREATED SUCCESSFULLY")
    print("Order:", order.id)
    print("Amount:", total)
    print("Currency:", settings.stripe_currency)
    print("Session:", session.id)
    print("=" * 70)

    return CheckoutResponse(
        order_id=order.id,
        amount=total,
        currency=settings.stripe_currency,
        checkout_session_id=session.id,
        checkout_url=session.url,
    )