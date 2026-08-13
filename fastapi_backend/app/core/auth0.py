from functools import lru_cache

import jwt

from jwt import PyJWKClient

from app.core.config import settings


@lru_cache
def get_jwks_client() -> PyJWKClient:

    return PyJWKClient(
        f"https://{settings.auth0_domain}/"
        ".well-known/jwks.json"
    )


def verify_auth0_access_token(
    token: str,
) -> dict:

    try:

        signing_key = (
            get_jwks_client()
            .get_signing_key_from_jwt(token)
        )

        payload = jwt.decode(
            token,

            signing_key.key,

            algorithms=["RS256"],

            audience=settings.auth0_audience,

            issuer=(
                f"https://"
                f"{settings.auth0_domain}/"
            ),

            # Allow a small difference between
            # Auth0 time and local computer time.
            leeway=60,
        )

        return payload

    except jwt.ExpiredSignatureError:

        raise ValueError(
            "Auth0 access token has expired"
        )

    except jwt.InvalidAudienceError:

        raise ValueError(
            "Invalid Auth0 access-token audience"
        )

    except jwt.InvalidIssuerError:

        raise ValueError(
            "Invalid Auth0 token issuer"
        )

    except jwt.PyJWTError as exc:

        raise ValueError(
            f"Invalid Auth0 access token: {exc}"
        )