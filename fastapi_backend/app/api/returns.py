from datetime import datetime
from datetime import timedelta

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.db.session import get_db

from app.models.order import Order
from app.models.order import OrderStatus

from app.models.return_request import (
    ReturnRequest,
    ReturnRequestStatus,
)

from app.schemas.return_request import (
    ReturnRequestCreate,
    ReturnRequestResponse,
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/orders",
    tags=["Returns"],
)


# ============================================================
# RETURN WINDOW
# ============================================================

RETURN_WINDOW_DAYS = 7


# ============================================================
# REQUEST RETURN
#
# POST /orders/{order_id}/return
# ============================================================

@router.post(
    "/{order_id}/return",
    response_model=ReturnRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def request_return(
    order_id: int,

    request: ReturnRequestCreate,

    current_user: CurrentUser,

    db: Session = Depends(get_db),
):

    # ========================================================
    # 1. GET USER ORDER
    # ========================================================

    order = db.scalar(
        select(Order).where(
            Order.id == order_id,
            Order.user_id == current_user.id,
        )
    )

    if not order:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    # ========================================================
    # 2. CHECK ORDER STATUS
    # ========================================================

    if order.order_status != OrderStatus.delivered:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Return can only be requested "
                "for delivered orders"
            ),
        )

    # ========================================================
    # 3. CHECK CREATED DATE
    # ========================================================

    if not order.created_at:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order creation date unavailable",
        )

    # ========================================================
    # 4. CHECK RETURN WINDOW
    # ========================================================

    return_deadline = (
        order.created_at
        + timedelta(
            days=RETURN_WINDOW_DAYS
        )
    )

    if datetime.utcnow() > return_deadline:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Return window of "
                f"{RETURN_WINDOW_DAYS} days has expired"
            ),
        )

    # ========================================================
    # 5. VALIDATE REASON
    # ========================================================

    reason = request.reason.strip()

    if not reason:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Return reason is required",
        )

    # ========================================================
    # 6. CLEAN COMMENT
    # ========================================================

    comment = None

    if request.comment:

        comment = request.comment.strip()

        if not comment:
            comment = None

    # ========================================================
    # 7. CHECK EXISTING REQUEST
    # ========================================================

    existing_request = db.scalar(
        select(ReturnRequest).where(
            ReturnRequest.order_id == order.id
        )
    )

    if existing_request:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Return request already exists "
                f"with status: "
                f"{existing_request.status.value}"
            ),
        )

    # ========================================================
    # 8. CREATE RETURN REQUEST
    # ========================================================

    return_request = ReturnRequest(

        order_id=order.id,

        user_id=current_user.id,

        reason=reason,

        comment=comment,

        status=ReturnRequestStatus.pending,
    )

    db.add(return_request)

    # ========================================================
    # 9. UPDATE ORDER STATUS
    # ========================================================

    order.order_status = (
        OrderStatus.return_requested
    )

    # ========================================================
    # 10. SAVE
    # ========================================================

    try:

        db.commit()

        db.refresh(
            return_request
        )

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create return request",
        ) from exc

    # ========================================================
    # 11. RESPONSE
    # ========================================================

    return return_request