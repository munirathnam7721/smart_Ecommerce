from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db

from app.models.user import User
from app.models.user import UserRole

from app.schemas.admin import (
    AdminUserResponse,
    AdminUserUpdate,
)


router = APIRouter(
    prefix="/admin/users",
    tags=["Admin - Users"],
)


# ============================================================
# GET ALL USERS
#
# GET /admin/users
# ============================================================

@router.get(
    "",
    response_model=list[AdminUserResponse],
)
def get_all_users(
    current_user=Depends(
        require_roles(UserRole.admin)
    ),
    db: Session = Depends(get_db),
):

    users = db.scalars(
        select(User)
        .order_by(
            User.id.desc()
        )
    ).all()

    return users


# ============================================================
# GET SINGLE USER
#
# GET /admin/users/{user_id}
# ============================================================

@router.get(
    "/{user_id}",
    response_model=AdminUserResponse,
)
def get_user(
    user_id: int,
    current_user=Depends(
        require_roles(UserRole.admin)
    ),
    db: Session = Depends(get_db),
):

    user = db.get(
        User,
        user_id,
    )

    if not user:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


# ============================================================
# UPDATE USER
#
# PUT /admin/users/{user_id}
# ============================================================

@router.put(
    "/{user_id}",
    response_model=AdminUserResponse,
)
def update_user(
    user_id: int,
    payload: AdminUserUpdate,
    current_user=Depends(
        require_roles(UserRole.admin)
    ),
    db: Session = Depends(get_db),
):

    user = db.get(
        User,
        user_id,
    )

    if not user:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # --------------------------------------------------------
    # UPDATE NAME
    # --------------------------------------------------------

    if payload.name is not None:

        name = payload.name.strip()

        if not name:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Name cannot be empty",
            )

        user.name = name

    # --------------------------------------------------------
    # UPDATE EMAIL
    # --------------------------------------------------------

    if payload.email is not None:

        new_email = str(
            payload.email
        ).lower().strip()

        existing_user = db.scalar(
            select(User).where(
                User.email == new_email,
                User.id != user_id,
            )
        )

        if existing_user:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists",
            )

        user.email = new_email

    # --------------------------------------------------------
    # UPDATE ROLE
    # --------------------------------------------------------

    if payload.role is not None:

        user.role = payload.role

    # --------------------------------------------------------
    # UPDATE ACTIVE STATUS
    # --------------------------------------------------------

    if payload.is_active is not None:

        user.is_active = payload.is_active

    db.commit()

    db.refresh(user)

    return user


# ============================================================
# CHANGE USER ROLE
#
# PATCH /admin/users/{user_id}/role
# ============================================================

@router.patch(
    "/{user_id}/role",
    response_model=AdminUserResponse,
)
def update_user_role(
    user_id: int,
    role: UserRole,
    current_user=Depends(
        require_roles(UserRole.admin)
    ),
    db: Session = Depends(get_db),
):

    user = db.get(
        User,
        user_id,
    )

    if not user:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.role = role

    db.commit()

    db.refresh(user)

    return user


# ============================================================
# ACTIVATE / DEACTIVATE USER
#
# PATCH /admin/users/{user_id}/status
# ============================================================

@router.patch(
    "/{user_id}/status",
    response_model=AdminUserResponse,
)
def update_user_status(
    user_id: int,
    is_active: bool,
    current_user=Depends(
        require_roles(UserRole.admin)
    ),
    db: Session = Depends(get_db),
):

    user = db.get(
        User,
        user_id,
    )

    if not user:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Prevent admin from accidentally deactivating
    # their own account.

    if (
        user.id == current_user.id
        and not is_active
    ):

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate your own account",
        )

    user.is_active = is_active

    db.commit()

    db.refresh(user)

    return user