from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.db.session import get_db

from app.models.notification import Notification

from app.schemas.notification import (
    NotificationResponse,
)

from app.services.notification_service import (
    create_notification,
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


# ============================================================
# GET NOTIFICATIONS
#
# GET /notifications
# ============================================================

@router.get(
    "",
    response_model=list[NotificationResponse],
)
def get_notifications(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):

    notifications = db.scalars(
        select(Notification)
        .where(
            Notification.user_id == current_user.id
        )
        .order_by(
            Notification.timestamp.desc()
        )
    ).all()

    return notifications


# ============================================================
# MARK NOTIFICATION AS READ
#
# POST /notifications/read?notification_id=1
# ============================================================

@router.post(
    "/read",
    response_model=NotificationResponse,
)
def mark_notification_read(
    notification_id: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):

    notification = db.scalar(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
    )

    if not notification:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    notification.read_status = True

    db.commit()

    db.refresh(notification)

    return notification


# ============================================================
# TEST NOTIFICATION
#
# POST /notifications/test
# ============================================================

@router.post(
    "/test",
    response_model=NotificationResponse,
)
def create_test_notification(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):

    notification = create_notification(
        db=db,
        user_id=current_user.id,
        notification_type="test",
        message="This is a test notification.",
    )

    db.commit()

    db.refresh(notification)

    return notification