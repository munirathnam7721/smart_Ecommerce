from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db

from app.models.product import Product
from app.models.user import UserRole

from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
)


router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


# ============================================================
# CREATE PRODUCT
# POST /products
# ADMIN ONLY
# ============================================================

@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(
            require_roles(UserRole.admin)
        )
    ]
)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db)
):

    product = Product(
        **payload.model_dump()
    )

    db.add(product)

    db.commit()

    db.refresh(product)

    return product


# ============================================================
# UPDATE PRODUCT
# PUT /products/{product_id}
# ADMIN ONLY
# ============================================================

@router.put(
    "/{product_id}",
    response_model=ProductResponse
)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(UserRole.admin)
    ),
):

    product = db.get(
        Product,
        product_id
    )

    if not product:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    update_data = payload.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():

        setattr(
            product,
            field,
            value
        )

    db.commit()

    db.refresh(product)

    return product


# ============================================================
# DELETE PRODUCT
# DELETE /products/{product_id}
# ADMIN ONLY
# ============================================================

@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(
            require_roles(UserRole.admin)
        )
    ]
)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):

    product = db.get(
        Product,
        product_id
    )

    if not product:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    db.delete(product)

    db.commit()

    return None


# ============================================================
# GET ALL PRODUCTS
# GET /products
# PUBLIC
# ============================================================

@router.get(
    "",
    response_model=list[ProductResponse]
)
def list_products(
    db: Session = Depends(get_db)
):

    return db.query(Product).all()


# ============================================================
# GET SINGLE PRODUCT
# GET /products/{product_id}
# PUBLIC
# ============================================================

@router.get(
    "/{product_id}",
    response_model=ProductResponse
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):

    product = db.get(
        Product,
        product_id
    )

    if not product:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return product