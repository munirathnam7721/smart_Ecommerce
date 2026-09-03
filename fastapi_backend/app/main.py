import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# ============================================================
# API ROUTERS
# ============================================================

from app.api.auth import router as auth_router
from app.api.products import router as products_router
from app.api.cart import router as cart_router
from app.api.checkout import router as checkout_router
from app.api.payment import router as payment_router
from app.api.webhook import router as webhook_router
from app.api.orders import router as orders_router
from app.api.returns import router as returns_router
from app.api.notifications import router as notifications_router

# ============================================================
# ADMIN ROUTERS
# ============================================================

from app.api.admin_orders import router as admin_orders_router
from app.api.admin_users import router as admin_users_router
from app.api.admin_products import router as admin_products_router
from app.api.admin_analytics import router as admin_analytics_router
from app.api.admin_reports import router as admin_reports_router
from app.api.admin_returns import router as admin_returns_router

# ============================================================
# EMAIL TEST
# ============================================================

from app.api.email_test import router as email_test_router

# ============================================================
# CONFIGURATION
# ============================================================

from app.core.config import settings

# ============================================================
# STRIPE EVENT MODEL
#
# IMPORTANT:
# This imports StripeEvent so SQLAlchemy knows about the
# stripe_events table.
# ============================================================

from app.models.stripe_event import StripeEvent

# ============================================================
# ORDER STATUS WORKER
# ============================================================

from app.services.order_status_worker import (
    update_order_statuses,
)


# ============================================================
# APPLICATION LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    print("=" * 70)
    print("SMART E-COMMERCE API STARTING")
    print("=" * 70)

    # --------------------------------------------------------
    # Start automatic order status worker
    # --------------------------------------------------------

    task = asyncio.create_task(
        update_order_statuses()
    )

    try:

        yield

    finally:

        print("=" * 70)
        print("SMART E-COMMERCE API SHUTTING DOWN")
        print("=" * 70)

        # ----------------------------------------------------
        # Stop worker
        # ----------------------------------------------------

        task.cancel()

        try:

            await task

        except asyncio.CancelledError:

            pass


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(

    title=settings.app_name,

    version="1.0.0",

    description=(
        "Smart E-Commerce Platform API"
    ),

    lifespan=lifespan,
)


# ============================================================
# STATIC FILES
# ============================================================

app.mount(

    "/static",

    StaticFiles(
        directory="static"
    ),

    name="static",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=settings.cors_origin_list,

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ============================================================
# AUTH
# ============================================================

app.include_router(
    auth_router
)


# ============================================================
# PRODUCTS
# ============================================================

app.include_router(
    products_router
)


# ============================================================
# CART
# ============================================================

app.include_router(
    cart_router
)


# ============================================================
# CHECKOUT
# ============================================================

app.include_router(
    checkout_router
)


# ============================================================
# PAYMENT
# ============================================================

app.include_router(
    payment_router
)


# ============================================================
# STRIPE WEBHOOK
# ============================================================

app.include_router(
    webhook_router
)


# ============================================================
# CUSTOMER ORDERS
# ============================================================

app.include_router(
    orders_router
)


# ============================================================
# CUSTOMER RETURNS
# ============================================================

app.include_router(
    returns_router
)


# ============================================================
# ADMIN USERS
# ============================================================

app.include_router(
    admin_users_router
)


# ============================================================
# ADMIN PRODUCTS
# ============================================================

app.include_router(
    admin_products_router
)


# ============================================================
# ADMIN ORDERS
# ============================================================

app.include_router(
    admin_orders_router
)


# ============================================================
# ADMIN RETURNS / REFUNDS
# ============================================================

app.include_router(
    admin_returns_router
)


# ============================================================
# ADMIN ANALYTICS
# ============================================================

app.include_router(
    admin_analytics_router
)


# ============================================================
# ADMIN REPORTS
# ============================================================

app.include_router(
    admin_reports_router
)


# ============================================================
# NOTIFICATIONS
# ============================================================

app.include_router(
    notifications_router
)


# ============================================================
# EMAIL TEST
# ============================================================

app.include_router(
    email_test_router
)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "ok"
    }


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {

        "message":
            "Smart E-Commerce API is running",

        "docs":
            "/docs",

        "status":
            "success",
    }