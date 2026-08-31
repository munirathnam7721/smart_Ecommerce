import stripe

from decimal import Decimal

from app.core.config import settings


# ============================================================
# STRIPE CONFIGURATION
# ============================================================

stripe.api_key = settings.stripe_secret_key


# ============================================================
# CREATE CHECKOUT SESSION
# ============================================================

def create_checkout_session(
    order_id: int,
    amount: Decimal,
    currency: str,
):
    """
    Create a Stripe Checkout Session.

    Amount is stored in major currency units.

    Example:

        INR 100.00
            ↓
        10000 paise
    """

    # --------------------------------------------------------
    # Normalize amount
    # --------------------------------------------------------

    amount = Decimal(
        str(amount)
    ).quantize(
        Decimal("0.01")
    )


    # --------------------------------------------------------
    # Validate amount
    # --------------------------------------------------------

    if amount <= 0:

        raise ValueError(
            "Checkout amount must be greater than zero"
        )


    # --------------------------------------------------------
    # Convert to smallest currency unit
    # --------------------------------------------------------

    amount_in_smallest_unit = int(
        amount * Decimal("100")
    )


    # --------------------------------------------------------
    # Debug information
    # --------------------------------------------------------

    print("=" * 60)
    print("CREATING STRIPE CHECKOUT SESSION")
    print("Order ID:", order_id)
    print("Amount:", amount)
    print(
        "Stripe Amount:",
        amount_in_smallest_unit,
    )
    print("Currency:", currency)
    print("=" * 60)


    # --------------------------------------------------------
    # Create Stripe Checkout Session
    # --------------------------------------------------------

    session = stripe.checkout.Session.create(

        mode="payment",

        payment_method_types=[
            "card"
        ],

        client_reference_id=str(
            order_id
        ),

        line_items=[
            {
                "price_data": {
                    "currency": currency.lower(),

                    "product_data": {
                        "name": (
                            "Smart E-Commerce "
                            f"Order #{order_id}"
                        ),
                    },

                    "unit_amount": (
                        amount_in_smallest_unit
                    ),
                },

                "quantity": 1,
            }
        ],

        # ----------------------------------------------------
        # IMPORTANT
        # ----------------------------------------------------
        # This metadata is later used by:
        #
        # GET /payment/verify
        #
        # to find the order.

        metadata={
            "order_id": str(
                order_id
            ),
        },

        # ----------------------------------------------------
        # Stripe redirects customer here after payment
        # ----------------------------------------------------

        success_url=(
            f"{settings.frontend_url}"
            "/payment/success"
            "?session_id={CHECKOUT_SESSION_ID}"
        ),

        # ----------------------------------------------------
        # Stripe redirects customer here if cancelled
        # ----------------------------------------------------

        cancel_url=(
            f"{settings.frontend_url}"
            "/payment/cancel"
        ),
    )


    # --------------------------------------------------------
    # Debug information
    # --------------------------------------------------------

    print("=" * 60)
    print("STRIPE CHECKOUT SESSION CREATED")
    print("Order ID:", order_id)
    print("Amount:", amount)
    print(
        "Stripe Amount:",
        amount_in_smallest_unit,
    )
    print("Currency:", currency)
    print("Session ID:", session.id)
    print("Session URL:", session.url)
    print("=" * 60)


    return session