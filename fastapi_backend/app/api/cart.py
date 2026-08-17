from decimal import Decimal

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser

from app.db.session import get_db

from app.models.cart import Cart
from app.models.product import Product

from app.models.user import UserRole

from app.schemas.cart import (
    CartCreate,
    CartItemResponse,
    CartResponse,
    CartUpdate,
)


router = APIRouter(
    prefix="/cart",
    tags=["Cart"]
)


TAX_RATE = Decimal("0.00")


def get_cart_item(
    cart_id: int,
    user_id: int,
    db: Session
):

    item = db.scalar(
        select(Cart).where(
            Cart.id == cart_id,
            Cart.user_id == user_id
        )
    )

    if not item:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )

    return item


def build_cart_response(
    user_id: int,
    db: Session
):

    items = db.scalars(
        select(Cart).where(
            Cart.user_id == user_id
        )
    ).all()

    response_items = []

    subtotal = Decimal("0.00")

    for item in items:

        product = db.get(
            Product,
            item.product_id
        )

        if not product:
            continue

        price = Decimal(
            str(product.price)
        )

        item_total = (
            price * item.quantity
        )

        subtotal += item_total

        response_items.append(
            CartItemResponse(
                id=item.id,
                user_id=item.user_id,
                product_id=item.product_id,
                product_name=product.name,
                price=price,
                quantity=item.quantity,
                item_total=item_total
            )
        )

    tax = (
        subtotal * TAX_RATE
    ).quantize(
        Decimal("0.01")
    )

    grand_total = (
        subtotal + tax
    ).quantize(
        Decimal("0.01")
    )

    return CartResponse(
        items=response_items,
        subtotal=subtotal.quantize(
            Decimal("0.01")
        ),
        tax=tax,
        grand_total=grand_total
    )


@router.post(
    "/add",
    response_model=CartItemResponse,
    status_code=status.HTTP_201_CREATED
)
def add_to_cart(
    payload: CartCreate,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):

    product = db.get(
        Product,
        payload.product_id
    )

    if not product:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    if payload.quantity > product.stock:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient stock"
        )

    item = db.scalar(
        select(Cart).where(
            Cart.user_id == current_user.id,
            Cart.product_id == payload.product_id
        )
    )

    if item:

        new_quantity = (
            item.quantity
            + payload.quantity
        )

        if new_quantity > product.stock:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient stock"
            )

        item.quantity = new_quantity

    else:

        item = Cart(
            user_id=current_user.id,
            product_id=payload.product_id,
            quantity=payload.quantity
        )

        db.add(item)

    db.commit()

    db.refresh(item)

    price = Decimal(
        str(product.price)
    )

    item_total = (
        price * item.quantity
    )

    return CartItemResponse(
        id=item.id,
        user_id=item.user_id,
        product_id=item.product_id,
        product_name=product.name,
        price=price,
        quantity=item.quantity,
        item_total=item_total
    )


@router.get(
    "",
    response_model=CartResponse
)
def get_cart(
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):

    return build_cart_response(
        current_user.id,
        db
    )


@router.put(
    "/update",
    response_model=CartItemResponse
)
def update_cart(
    payload: CartUpdate,
    cart_id: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):

    item = get_cart_item(
        cart_id,
        current_user.id,
        db
    )

    product = db.get(
        Product,
        item.product_id
    )

    if not product:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    if payload.quantity > product.stock:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient stock"
        )

    item.quantity = payload.quantity

    db.commit()

    db.refresh(item)

    price = Decimal(
        str(product.price)
    )

    item_total = (
        price * item.quantity
    )

    return CartItemResponse(
        id=item.id,
        user_id=item.user_id,
        product_id=item.product_id,
        product_name=product.name,
        price=price,
        quantity=item.quantity,
        item_total=item_total
    )


@router.delete(
    "/remove",
    status_code=status.HTTP_204_NO_CONTENT
)
def remove_from_cart(
    cart_id: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):

    item = get_cart_item(
        cart_id,
        current_user.id,
        db
    )

    db.delete(item)

    db.commit()

    return None