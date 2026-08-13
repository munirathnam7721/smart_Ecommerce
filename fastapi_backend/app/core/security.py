from datetime import datetime
from datetime import timedelta
from datetime import timezone

from typing import Any

import jwt

from pwdlib import PasswordHash

from app.core.config import settings


password_hash = PasswordHash.recommended()


def hash_password(password: str):

    return password_hash.hash(password)


def verify_password(
    password: str,
    hashed_password: str
):

    return password_hash.verify(
        password,
        hashed_password
    )


def create_token(
    subject: str,
    token_type: str,
    expires_delta: timedelta
):

    now = datetime.now(timezone.utc)

    payload: dict[str, Any] = {

        "sub": subject,

        "type": token_type,

        "iat": now,

        "exp": now + expires_delta,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )


def create_access_token(user_id: int):

    return create_token(
        str(user_id),
        "access",
        timedelta(
            minutes=settings.access_token_expire_minutes
        )
    )


def create_refresh_token(user_id: int):

    return create_token(
        str(user_id),
        "refresh",
        timedelta(
            days=settings.refresh_token_expire_days
        )
    )


def decode_local_token(token: str):

    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[
            settings.jwt_algorithm
        ]
    )
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token"
)