from collections.abc import Callable
from typing import Annotated

import jwt

from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session

from app.core.security import decode_local_token
from app.db.session import get_db

from app.models.user import User
from app.models.user import UserRole


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token"
)


DbSession = Annotated[
    Session,
    Depends(get_db)
]


def get_current_user(
    token: Annotated[
        str,
        Depends(oauth2_scheme)
    ],
    db: DbSession,
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired access token",
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )

    try:

        payload = decode_local_token(token)

        if payload.get("type") != "access":
            raise credentials_exception

        user_id = payload.get("sub")

        if not user_id:
            raise credentials_exception

        user = db.get(
            User,
            int(user_id)
        )

        if not user:
            raise credentials_exception

        # ====================================================
        # CHECK ACCOUNT STATUS
        # ====================================================

        if not user.is_active:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )

        return user

    except (
        jwt.InvalidTokenError,
        ValueError
    ):

        raise credentials_exception


CurrentUser = Annotated[
    User,
    Depends(get_current_user)
]


def require_roles(
    *allowed_roles: UserRole
) -> Callable:

    def dependency(
        current_user: CurrentUser
    ):

        if current_user.role not in allowed_roles:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You do not have permission "
                    "to access this resource"
                ),
            )

        return current_user

    return dependency