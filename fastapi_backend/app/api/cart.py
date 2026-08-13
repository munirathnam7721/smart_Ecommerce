from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.api.deps import require_roles

from app.db.session import get_db

from app.models.cart import Cart
from app.models.product import Product
from app.models.user import UserRole

from app.schemas.cart import (
    CartCreate,
    CartResponse,
    CartUpdate,
)


router = APIRouter(
    prefix="/cart",
    tags=["Cart"]
)


# ============================================================
# ADD PRODUCT TO CART
# POST /cart
# CUSTOMER / ADMIN
# ============================================================

@router.post(
    "",
    response_model=CartResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(
            require_roles(
                UserRole.customer,
                UserRole.admin
            )
        )
    ]
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

    return item


# ============================================================
# GET MY CART
# GET /cart
# CUSTOMER / ADMIN
# ============================================================

@router.get(
    "",
    response_model=list[CartResponse]
)
def get_my_cart(
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):

    return db.scalars(
        select(Cart).where(
            Cart.user_id == current_user.id
        )
    ).all()


# ============================================================
# UPDATE CART ITEM
# PUT /cart/{cart_id}
# CUSTOMER / ADMIN
# ============================================================

@router.put(
    "/{cart_id}",
    response_model=CartResponse
)
def update_cart_item(
    cart_id: int,
    payload: CartUpdate,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):

    item = db.get(
        Cart,
        cart_id
    )

    if not item:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )

    if item.user_id != current_user.id:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this cart item"
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

    return item


# ============================================================
# DELETE CART ITEM
# DELETE /cart/{cart_id}
# CUSTOMER / ADMIN
# ============================================================

@router.delete(
    "/{cart_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_cart_item(
    cart_id: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):

    item = db.get(
        Cart,
        cart_id
    )

    if not item:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )

    if item.user_id != current_user.id:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this cart item"
        )

    db.delete(item)

    db.commit()

    return None