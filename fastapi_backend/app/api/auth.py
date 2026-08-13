import jwt

from typing import Optional
from urllib.parse import urlencode

import requests

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser

from app.core.auth0 import verify_auth0_access_token
from app.core.config import settings

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_local_token,
    hash_password,
    verify_password,
)

from app.db.session import get_db

from app.models.user import User
from app.models.user import UserRole

from app.schemas.auth import (
    Auth0LoginRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# ============================================================
# HELPER
# ============================================================

def build_token_response(user: User) -> TokenResponse:

    return TokenResponse(
        access_token=create_access_token(
            user.id
        ),

        refresh_token=create_refresh_token(
            user.id
        ),

        expires_in=30 * 60,

        user=UserResponse.model_validate(
            user
        ),
    )


# ============================================================
# REGISTER
# POST /auth/register
# ============================================================

@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
):

    email = payload.email.lower().strip()

    existing_user = db.scalar(
        select(User).where(
            User.email == email
        )
    )

    if existing_user:

        raise HTTPException(
            status_code=409,
            detail="Email is already registered",
        )

    user = User(
        name=payload.name.strip(),

        email=email,

        password_hash=hash_password(
            payload.password
        ),

        role=UserRole.customer,
    )

    db.add(user)

    db.commit()

    db.refresh(user)

    return build_token_response(user)


# ============================================================
# NORMAL LOGIN
# POST /auth/login
# ============================================================

@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):

    email = payload.email.lower().strip()

    user = db.scalar(
        select(User).where(
            User.email == email
        )
    )

    if not user or not user.password_hash:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    if not verify_password(
        payload.password,
        user.password_hash,
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    return build_token_response(user)


# ============================================================
# SWAGGER LOGIN
# POST /auth/token
# ============================================================

@router.post(
    "/token",
)
def token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):

    email = form_data.username.lower().strip()

    user = db.scalar(
        select(User).where(
            User.email == email
        )
    )

    if not user or not user.password_hash:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    if not verify_password(
        form_data.password,
        user.password_hash,
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    access_token = create_access_token(
        user.id
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


# ============================================================
# REFRESH TOKEN
# POST /auth/refresh
# ============================================================

@router.post(
    "/refresh",
    response_model=TokenResponse,
)
def refresh(
    payload: RefreshRequest,
    db: Session = Depends(get_db),
):

    try:

        token_payload = decode_local_token(
            payload.refresh_token
        )

        if token_payload.get("type") != "refresh":

            raise ValueError()

        user_id = int(
            token_payload["sub"]
        )

    except (
        jwt.InvalidTokenError,
        KeyError,
        ValueError,
        TypeError,
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token",
        )

    user = db.get(
        User,
        user_id
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="User no longer exists",
        )

    return build_token_response(user)


# ============================================================
# CURRENT USER
# GET /auth/me
# ============================================================

@router.get(
    "/me",
    response_model=UserResponse,
)
def me(
    current_user: CurrentUser,
):

    return current_user


# ============================================================
# AUTH0 LOGIN START
# GET /auth/auth0/login
# ============================================================

@router.get(
    "/auth0/login",
)
def auth0_login_start():

    redirect_uri = (
        "http://localhost:8000/auth/auth0/callback"
    )

    params = {
        "response_type": "code",

        "client_id":
            settings.auth0_client_id,

        "redirect_uri":
            redirect_uri,

        "audience":
            settings.auth0_audience,

        "scope":
            "openid profile email",

        "connection":
            "google-oauth2",
    }

    auth_url = (
        f"https://{settings.auth0_domain}"
        "/authorize?"
        + urlencode(params)
    )

    return RedirectResponse(
        url=auth_url
    )


# ============================================================
# AUTH0 CALLBACK
# GET /auth/auth0/callback
# ============================================================

@router.get(
    "/auth0/callback",
)
def auth0_callback(
    code: Optional[str] = None,

    error: Optional[str] = None,

    error_description: Optional[str] = None,

    db: Session = Depends(get_db),
):

    # --------------------------------------------------------
    # Auth0 returned an error
    # --------------------------------------------------------

    if error:

        raise HTTPException(
            status_code=400,

            detail={
                "error": error,

                "error_description":
                    error_description,
            },
        )

    # --------------------------------------------------------
    # Authorization code missing
    # --------------------------------------------------------

    if not code:

        raise HTTPException(
            status_code=400,

            detail=(
                "Auth0 did not return "
                "an authorization code"
            ),
        )

    # --------------------------------------------------------
    # Auth0 token endpoint
    # --------------------------------------------------------

    token_url = (
        f"https://{settings.auth0_domain}"
        "/oauth/token"
    )

    redirect_uri = (
        "http://localhost:8000/auth/auth0/callback"
    )

    token_data = {

        "grant_type":
            "authorization_code",

        "client_id":
            settings.auth0_client_id,

        "client_secret":
            settings.auth0_client_secret,

        "code":
            code,

        "redirect_uri":
            redirect_uri,
    }

    # --------------------------------------------------------
    # Exchange authorization code for tokens
    # --------------------------------------------------------

    try:

        response = requests.post(
            token_url,

            json=token_data,

            timeout=10,
        )

    except requests.RequestException as exc:

        raise HTTPException(
            status_code=502,

            detail=(
                "Could not connect to Auth0: "
                f"{str(exc)}"
            ),
        )

    # --------------------------------------------------------
    # Auth0 rejected authorization code
    # --------------------------------------------------------

    if response.status_code != 200:

        try:

            auth0_error = response.json()

        except ValueError:

            auth0_error = response.text

        raise HTTPException(
            status_code=401,

            detail={
                "message":
                    "Auth0 token exchange failed",

                "auth0_response":
                    auth0_error,
            },
        )

    # --------------------------------------------------------
    # Parse token response
    # --------------------------------------------------------

    try:

        token_json = response.json()

    except ValueError:

        raise HTTPException(
            status_code=502,

            detail=(
                "Invalid response received "
                "from Auth0"
            ),
        )

    # --------------------------------------------------------
    # Get Auth0 access token
    # --------------------------------------------------------

    auth0_access_token = token_json.get(
        "access_token"
    )

    if not auth0_access_token:

        raise HTTPException(
            status_code=401,

            detail=(
                "Auth0 access token "
                "missing from response"
            ),
        )

    # --------------------------------------------------------
    # Validate Auth0 API access token
    #
    # This verifies:
    # - signature
    # - issuer
    # - audience
    # - expiration
    # --------------------------------------------------------

    try:

        auth0_payload = (
            verify_auth0_access_token(
                auth0_access_token
            )
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=401,

            detail=str(exc),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=401,

            detail=(
                "Auth0 token validation failed: "
                f"{str(exc)}"
            ),
        )

    # --------------------------------------------------------
    # Get Auth0 subject
    # --------------------------------------------------------

    auth0_sub = auth0_payload.get(
        "sub"
    )

    if not auth0_sub:

        raise HTTPException(
            status_code=401,

            detail="Auth0 subject missing",
        )

    # --------------------------------------------------------
    # Get user profile from Auth0 /userinfo
    #
    # The API access token may not contain email.
    # /userinfo gives us the user's OIDC profile.
    # --------------------------------------------------------

    userinfo_url = (
        f"https://{settings.auth0_domain}"
        "/userinfo"
    )

    try:

        userinfo_response = requests.get(
            userinfo_url,

            headers={
                "Authorization":
                    f"Bearer {auth0_access_token}"
            },

            timeout=10,
        )

    except requests.RequestException as exc:

        raise HTTPException(
            status_code=502,

            detail=(
                "Could not connect to Auth0 "
                "userinfo endpoint: "
                f"{str(exc)}"
            ),
        )

    # --------------------------------------------------------
    # Auth0 /userinfo failed
    # --------------------------------------------------------

    if userinfo_response.status_code != 200:

        try:

            userinfo_error = (
                userinfo_response.json()
            )

        except ValueError:

            userinfo_error = (
                userinfo_response.text
            )

        raise HTTPException(
            status_code=401,

            detail={
                "message":
                    "Auth0 userinfo request failed",

                "auth0_response":
                    userinfo_error,
            },
        )

    # --------------------------------------------------------
    # Parse user profile
    # --------------------------------------------------------

    try:

        userinfo = (
            userinfo_response.json()
        )

    except ValueError:

        raise HTTPException(
            status_code=502,

            detail=(
                "Invalid response from "
                "Auth0 userinfo endpoint"
            ),
        )

    # --------------------------------------------------------
    # Auth0 subject from userinfo
    # --------------------------------------------------------

    userinfo_sub = userinfo.get(
        "sub"
    )

    if userinfo_sub:

        auth0_sub = userinfo_sub

    # --------------------------------------------------------
    # Get email
    # --------------------------------------------------------

    email = userinfo.get(
        "email"
    )

    if not email:

        raise HTTPException(
            status_code=400,

            detail=(
                "Email missing from "
                "Auth0 user profile"
            ),
        )

    # --------------------------------------------------------
    # Get name
    # --------------------------------------------------------

    name = (

        userinfo.get("name")

        or userinfo.get("nickname")

        or userinfo.get("given_name")

        or "Auth0 User"
    )

    # --------------------------------------------------------
    # Find user by Auth0 subject
    # --------------------------------------------------------

    user = db.scalar(
        select(User).where(
            User.auth0_sub == auth0_sub
        )
    )

    # --------------------------------------------------------
    # If Auth0 user doesn't exist,
    # search by email.
    # --------------------------------------------------------

    if not user:

        user = db.scalar(
            select(User).where(
                User.email ==
                email.lower().strip()
            )
        )

    # --------------------------------------------------------
    # Create new Auth0 user
    # --------------------------------------------------------

    if not user:

        user = User(

            name=name,

            email=email.lower().strip(),

            password_hash=None,

            role=UserRole.customer,

            auth0_sub=auth0_sub,
        )

        db.add(user)

    # --------------------------------------------------------
    # Existing user
    # --------------------------------------------------------

    else:

        user.auth0_sub = auth0_sub

        if name:

            user.name = name

    # --------------------------------------------------------
    # Save user
    # --------------------------------------------------------

    db.commit()

    db.refresh(user)

    # --------------------------------------------------------
    # Return YOUR application's JWT tokens
    # --------------------------------------------------------

    return build_token_response(user)


# ============================================================
# AUTH0 TOKEN LOGIN
# POST /auth/auth0
#
# Allows frontend/mobile clients that already have an
# Auth0 access token to exchange it for your local JWT.
# ============================================================

@router.post(
    "/auth0",
    response_model=TokenResponse,
)
def auth0_login(
    payload: Auth0LoginRequest,

    db: Session = Depends(get_db),
):

    # --------------------------------------------------------
    # Validate Auth0 access token
    # --------------------------------------------------------

    try:

        auth0_payload = (
            verify_auth0_access_token(
                payload.access_token
            )
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=401,

            detail=str(exc),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=401,

            detail=(
                "Auth0 token validation failed: "
                f"{str(exc)}"
            ),
        )

    # --------------------------------------------------------
    # Get Auth0 subject
    # --------------------------------------------------------

    auth0_sub = auth0_payload.get(
        "sub"
    )

    if not auth0_sub:

        raise HTTPException(
            status_code=401,

            detail="Auth0 subject missing",
        )

    # --------------------------------------------------------
    # Get profile from /userinfo
    # --------------------------------------------------------

    userinfo_url = (
        f"https://{settings.auth0_domain}"
        "/userinfo"
    )

    try:

        userinfo_response = requests.get(
            userinfo_url,

            headers={
                "Authorization":
                    f"Bearer {payload.access_token}"
            },

            timeout=10,
        )

    except requests.RequestException as exc:

        raise HTTPException(
            status_code=502,

            detail=(
                "Could not connect to Auth0 "
                "userinfo endpoint: "
                f"{str(exc)}"
            ),
        )

    if userinfo_response.status_code != 200:

        try:

            userinfo_error = (
                userinfo_response.json()
            )

        except ValueError:

            userinfo_error = (
                userinfo_response.text
            )

        raise HTTPException(
            status_code=401,

            detail={
                "message":
                    "Auth0 userinfo request failed",

                "auth0_response":
                    userinfo_error,
            },
        )

    userinfo = userinfo_response.json()

    # --------------------------------------------------------
    # Get profile
    # --------------------------------------------------------

    email = userinfo.get(
        "email"
    )

    name = (

        userinfo.get("name")

        or userinfo.get("nickname")

        or userinfo.get("given_name")

        or "Auth0 User"
    )

    if not email:

        raise HTTPException(
            status_code=400,

            detail=(
                "Email missing from "
                "Auth0 user profile"
            ),
        )

    # --------------------------------------------------------
    # Find user by Auth0 subject
    # --------------------------------------------------------

    user = db.scalar(
        select(User).where(
            User.auth0_sub == auth0_sub
        )
    )

    # --------------------------------------------------------
    # Search by email if needed
    # --------------------------------------------------------

    if not user:

        user = db.scalar(
            select(User).where(
                User.email ==
                email.lower().strip()
            )
        )

    # --------------------------------------------------------
    # Create user
    # --------------------------------------------------------

    if not user:

        user = User(

            name=name,

            email=email.lower().strip(),

            password_hash=None,

            role=UserRole.customer,

            auth0_sub=auth0_sub,
        )

        db.add(user)

    # --------------------------------------------------------
    # Existing user
    # --------------------------------------------------------

    else:

        user.auth0_sub = auth0_sub

        if name:

            user.name = name

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    db.commit()

    db.refresh(user)

    # --------------------------------------------------------
    # Return local JWT
    # --------------------------------------------------------

    return build_token_response(user)