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

    amount = Decimal(
        str(amount)
    ).quantize(
        Decimal("0.01")
    )

    if amount <= 0:
        raise ValueError(
            "Checkout amount must be greater than zero"
        )

    amount_in_smallest_unit = int(
        amount * Decimal("100")
    )

    print("=" * 70)
    print("CREATING STRIPE CHECKOUT SESSION")
    print("Order ID:", order_id)
    print("Amount:", amount)
    print(
        "Stripe Amount:",
        amount_in_smallest_unit,
    )
    print("Currency:", currency)
    print("=" * 70)

    session = stripe.checkout.Session.create(

        mode="payment",

        payment_method_types=[
            "card",
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

                    "unit_amount":
                        amount_in_smallest_unit,
                },

                "quantity": 1,
            }
        ],

        metadata={
            "order_id": str(order_id),
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

    print("=" * 70)
    print("STRIPE CHECKOUT SESSION CREATED")
    print("Order ID:", order_id)
    print("Session ID:", session.id)
    print("Session URL:", session.url)
    print("Payment Intent:", session.payment_intent)
    print("=" * 70)

    return session


# ============================================================
# GET CHECKOUT SESSION
# ============================================================

def get_checkout_session(
    session_id: str,
):

    if not session_id:

        raise ValueError(
            "Stripe session ID is required"
        )

    return stripe.checkout.Session.retrieve(
        session_id
    )


# ============================================================
# GET PAYMENT INTENT
# ============================================================

def get_payment_intent(
    payment_intent_id: str,
):

    if not payment_intent_id:

        raise ValueError(
            "Stripe Payment Intent ID is required"
        )

    return stripe.PaymentIntent.retrieve(
        payment_intent_id
    )


# ============================================================
# REFUND PAYMENT
# ============================================================

def create_refund(
    payment_intent_id: str,
    amount: Decimal | None = None,
):

    if not payment_intent_id:

        raise ValueError(
            "Payment Intent ID is required for refund"
        )

    # --------------------------------------------------------
    # FULL REFUND
    # --------------------------------------------------------

    if amount is None:

        print("=" * 70)
        print("CREATING FULL STRIPE REFUND")
        print(
            "Payment Intent:",
            payment_intent_id,
        )
        print("=" * 70)

        refund = stripe.Refund.create(

            payment_intent=payment_intent_id,
        )

        print("=" * 70)
        print("STRIPE REFUND CREATED")
        print("Refund ID:", refund.id)
        print("Status:", refund.status)
        print("=" * 70)

        return refund

    # --------------------------------------------------------
    # PARTIAL REFUND
    # --------------------------------------------------------

    amount = Decimal(
        str(amount)
    ).quantize(
        Decimal("0.01")
    )

    if amount <= 0:

        raise ValueError(
            "Refund amount must be greater than zero"
        )

    amount_in_smallest_unit = int(
        amount * Decimal("100")
    )

    print("=" * 70)
    print("CREATING PARTIAL STRIPE REFUND")
    print("Payment Intent:", payment_intent_id)
    print("Amount:", amount)
    print(
        "Stripe Amount:",
        amount_in_smallest_unit,
    )
    print("=" * 70)

    refund = stripe.Refund.create(

        payment_intent=payment_intent_id,

        amount=amount_in_smallest_unit,
    )

    print("=" * 70)
    print("STRIPE REFUND CREATED")
    print("Refund ID:", refund.id)
    print("Status:", refund.status)
    print("=" * 70)

    return refund


# ============================================================
# GET REFUND
# ============================================================

def get_refund(
    refund_id: str,
):

    if not refund_id:

        raise ValueError(
            "Refund ID is required"
        )

    return stripe.Refund.retrieve(
        refund_id
    )