from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import status

from sqlalchemy import select
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


@router.get(
    "/category/{category}",
    response_model=list[ProductResponse]
)
def products_by_category(
    category: str,
    db: Session = Depends(get_db)
):

    statement = (
        select(Product)
        .where(
            Product.category == category
        )
    )

    return db.scalars(statement).all()


@router.get(
    "",
    response_model=list[ProductResponse]
)
def list_products(
    category: str | None = Query(
        default=None
    ),
    min_price: float | None = Query(
        default=None,
        ge=0
    ),
    max_price: float | None = Query(
        default=None,
        ge=0
    ),
    in_stock: bool | None = Query(
        default=None
    ),
    sort: str | None = Query(
        default=None
    ),
    db: Session = Depends(get_db)
):

    statement = select(Product)

    if category:
        statement = statement.where(
            Product.category == category
        )

    if min_price is not None:
        statement = statement.where(
            Product.price >= min_price
        )

    if max_price is not None:
        statement = statement.where(
            Product.price <= max_price
        )

    if in_stock is True:
        statement = statement.where(
            Product.stock > 0
        )

    elif in_stock is False:
        statement = statement.where(
            Product.stock == 0
        )

    if sort == "popularity":
        statement = statement.order_by(
            Product.popularity.desc()
        )

    elif sort == "price_asc":
        statement = statement.order_by(
            Product.price.asc()
        )

    elif sort == "price_desc":
        statement = statement.order_by(
            Product.price.desc()
        )

    elif sort == "name":
        statement = statement.order_by(
            Product.name.asc()
        )

    return db.scalars(statement).all()


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