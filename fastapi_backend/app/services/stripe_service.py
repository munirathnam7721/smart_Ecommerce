import stripe

from decimal import Decimal

from app.core.config import settings


stripe.api_key = settings.stripe_secret_key


def create_checkout_session(
    order_id: int,
    amount: Decimal,
    currency: str,
):
    """
    Create a Stripe Checkout Session for an order.

    Stripe expects the amount in the smallest currency unit.
    For INR, this is paise.
    """

    amount_in_smallest_unit = int(
        amount * Decimal("100")
    )

    session = stripe.checkout.Session.create(

        mode="payment",

        payment_method_types=[
            "card"
        ],

        line_items=[
            {
                "price_data": {
                    "currency": currency,

                    "product_data": {
                        "name": (
                            f"Order #{order_id}"
                        ),
                    },

                    "unit_amount":
                        amount_in_smallest_unit,
                },

                "quantity": 1,
            }
        ],

        metadata={
            "order_id": str(order_id)
        },

        success_url=(
            f"{settings.frontend_url}"
            "/payment/success"
            "?session_id={CHECKOUT_SESSION_ID}"
        ),

        cancel_url=(
            f"{settings.frontend_url}"
            "/payment/cancel"
        ),
    )

    return session