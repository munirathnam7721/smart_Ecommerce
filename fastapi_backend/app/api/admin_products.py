import os
import uuid

from fastapi import APIRouter
from fastapi import Depends
from fastapi import File
from fastapi import HTTPException
from fastapi import UploadFile
from fastapi import status

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db

from app.models.product import Product
from app.models.user import UserRole

from app.schemas.admin import (
    AdminProductCreate,
    AdminProductUpdate,
)


router = APIRouter(
    prefix="/admin/products",
    tags=["Admin - Products"],
)


UPLOAD_DIR = os.path.join(
    "static",
    "products",
)

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True,
)


ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


# ============================================================
# GET ALL PRODUCTS
# ============================================================

@router.get("")
def get_all_products(
    current_user=Depends(
        require_roles(UserRole.admin)
    ),
    db: Session = Depends(get_db),
):

    return db.scalars(
        select(Product)
        .order_by(
            Product.id.desc()
        )
    ).all()


# ============================================================
# CREATE PRODUCT
# ============================================================

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    payload: AdminProductCreate,
    current_user=Depends(
        require_roles(UserRole.admin)
    ),
    db: Session = Depends(get_db),
):

    if payload.price < 0:
        raise HTTPException(
            status_code=400,
            detail="Price cannot be negative",
        )

    if payload.stock < 0:
        raise HTTPException(
            status_code=400,
            detail="Stock cannot be negative",
        )

    product = Product(
        name=payload.name.strip(),
        description=payload.description,
        price=payload.price,
        stock=payload.stock,
    )

    db.add(product)

    db.commit()

    db.refresh(product)

    return product


# ============================================================
# UPDATE PRODUCT
# ============================================================

@router.put(
    "/{product_id}",
)
def update_product(
    product_id: int,
    payload: AdminProductUpdate,
    current_user=Depends(
        require_roles(UserRole.admin)
    ),
    db: Session = Depends(get_db),
):

    product = db.get(
        Product,
        product_id,
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    if payload.name is not None:
        product.name = payload.name.strip()

    if payload.description is not None:
        product.description = payload.description

    if payload.price is not None:

        if payload.price < 0:
            raise HTTPException(
                status_code=400,
                detail="Price cannot be negative",
            )

        product.price = payload.price

    if payload.stock is not None:

        if payload.stock < 0:
            raise HTTPException(
                status_code=400,
                detail="Stock cannot be negative",
            )

        product.stock = payload.stock

    db.commit()

    db.refresh(product)

    return product


# ============================================================
# DELETE PRODUCT
# ============================================================

@router.delete(
    "/{product_id}",
)
def delete_product(
    product_id: int,
    current_user=Depends(
        require_roles(UserRole.admin)
    ),
    db: Session = Depends(get_db),
):

    product = db.get(
        Product,
        product_id,
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    db.delete(product)

    db.commit()

    return {
        "message": "Product deleted successfully",
        "product_id": product_id,
    }


# ============================================================
# UPLOAD PRODUCT IMAGE
# ============================================================

@router.post(
    "/{product_id}/image",
)
async def upload_product_image(
    product_id: int,
    file: UploadFile = File(...),
    current_user=Depends(
        require_roles(UserRole.admin)
    ),
    db: Session = Depends(get_db),
):

    product = db.get(
        Product,
        product_id,
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                "Only JPEG, PNG and WebP "
                "images are allowed"
            ),
        )

    extension = os.path.splitext(
        file.filename or ""
    )[1].lower()

    if not extension:
        extension = ".jpg"

    filename = (
        f"{uuid.uuid4().hex}"
        f"{extension}"
    )

    file_path = os.path.join(
        UPLOAD_DIR,
        filename,
    )

    with open(
        file_path,
        "wb",
    ) as output:

        while True:

            chunk = await file.read(
                1024 * 1024
            )

            if not chunk:
                break

            output.write(chunk)

    product.image_url = (
        f"/static/products/{filename}"
    )

    db.commit()

    db.refresh(product)

    return {
        "message": "Product image uploaded",
        "product_id": product.id,
        "image_url": product.image_url,
    }


# ============================================================
# UPDATE STOCK ONLY
# ============================================================

@router.patch(
    "/{product_id}/stock",
)
def update_stock(
    product_id: int,
    stock: int,
    current_user=Depends(
        require_roles(UserRole.admin)
    ),
    db: Session = Depends(get_db),
):

    if stock < 0:
        raise HTTPException(
            status_code=400,
            detail="Stock cannot be negative",
        )

    product = db.get(
        Product,
        product_id,
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    product.stock = stock

    db.commit()

    db.refresh(product)

    return {
        "product_id": product.id,
        "stock": product.stock,
    }