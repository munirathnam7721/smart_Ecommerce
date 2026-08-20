from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.products import router as products_router
from app.api.cart import router as cart_router
from app.api.checkout import router as checkout_router
from app.api.orders import router as orders_router

from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Smart E-Commerce Platform API"
)


app.add_middleware(
    CORSMiddleware,

    allow_origins=settings.cors_origin_list,

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# Authentication
app.include_router(
    auth_router
)


# Products
app.include_router(
    products_router
)


# Cart
app.include_router(
    cart_router
)


# Checkout
app.include_router(
    checkout_router
)


# Orders
app.include_router(
    orders_router
)


@app.get("/health")
def health():

    return {
        "status": "ok"
    }


@app.get("/")
def root():

    return {
        "message": "Smart E-Commerce API is running",
        "docs": "/docs",
        "status": "success"
    }