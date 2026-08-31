from functools import lru_cache

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):

    # -----------------------------
    # Application
    # -----------------------------

    app_name: str = "Smart E-Commerce API"

    environment: str = "development"

    # -----------------------------
    # Database
    # -----------------------------

    database_url: str

    # -----------------------------
    # JWT
    # -----------------------------

    jwt_secret_key: str

    jwt_algorithm: str = "HS256"

    access_token_expire_minutes: int = 30

    refresh_token_expire_days: int = 7

    # -----------------------------
    # Auth0
    # -----------------------------

    auth0_domain: str

    auth0_audience: str

    auth0_client_id: str

    auth0_client_secret: str

    # -----------------------------
    # CORS
    # -----------------------------

    cors_origins: str = (
        "http://localhost:3000,"
        "http://localhost:5173"
    )

    # -----------------------------
    # Stripe
    # -----------------------------

    stripe_secret_key: str

    stripe_webhook_secret: str = ""

    stripe_currency: str = "inr"

    frontend_url: str = (
        "http://localhost:5173"
    )

    # -----------------------------
    # Email / SMTP
    # -----------------------------

    smtp_host: str = "smtp.gmail.com"

    smtp_port: int = 587

    smtp_username: str

    smtp_password: str

    smtp_from_email: str

    smtp_from_name: str = (
        "Smart E-Commerce"
    )

    # -----------------------------
    # Pydantic Settings
    # -----------------------------

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    # -----------------------------
    # CORS helper
    # -----------------------------

    @property
    def cors_origin_list(self):

        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

    # -----------------------------
    # Auth0 issuer
    # -----------------------------

    @property
    def auth0_issuer(self):

        return (
            f"https://{self.auth0_domain}/"
        )


@lru_cache
def get_settings():

    return Settings()


settings = get_settings()