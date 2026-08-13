from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    app_name: str = "Smart E-Commerce API"

    environment: str = "development"

    database_url: str

    jwt_secret_key: str

    jwt_algorithm: str = "HS256"

    access_token_expire_minutes: int = 30

    refresh_token_expire_days: int = 7

    auth0_domain: str

    auth0_audience: str
    auth0_client_id: str
    auth0_client_secret: str

    cors_origins: str = (
        "http://localhost:3000,http://localhost:5173"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origin_list(self):

        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

    @property
    def auth0_issuer(self):

        return f"https://{self.auth0_domain}/"


@lru_cache
def get_settings():

    return Settings()


settings = get_settings()