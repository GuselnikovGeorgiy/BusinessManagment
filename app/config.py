from pathlib import Path
from typing import List

from dotenv import load_dotenv
from pydantic import computed_field, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent  # корень проекта
ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH)


class AuthJWTSettings(BaseSettings):
    """Параметры для подписи и проверки JWT‑токенов."""
    private_key_path: Path = Field(
        default=BASE_DIR / "utils" / "certs" / "jwt-private.pem"
    )
    public_key_path: Path = Field(
        default=BASE_DIR / "utils" / "certs" / "jwt-public.pem"
    )
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 600

    model_config = SettingsConfigDict(env_prefix="JWT_")


class Settings(BaseSettings):
    DB_NAME: str
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str

    REDIS_HOST: str
    REDIS_PORT: int

    CACHE_PREFIX: str = "cache"

    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000"],
        description="Список разрешённых источников CORS"
    )

    auth_jwt: AuthJWTSettings = Field(default_factory=AuthJWTSettings)

    @computed_field
    def DATABASE_URL(self) -> str:  # noqa: N802 (по требованиям Pydantic v2)
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @field_validator("ALLOWED_ORIGINS", mode='before')
    def split_origins(cls, v):
        """Разрешить передавать список через запятую в .env"""
        if isinstance(v, str):
            return [orig.strip() for orig in v.split(",") if orig.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        extra="ignore",
    )


settings = Settings()
