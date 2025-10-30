import os

from dotenv import load_dotenv
from functools import lru_cache
from pydantic import PostgresDsn, AmqpDsn
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    secret_key: str = os.getenv("SECRET_KEY")
    auth_algorithm: str = os.getenv("AUTH_ALGORITHM", "HS256")
    access_token_ttl_minutes: int = int(os.getenv("ACCESS_TOKEN_TTL_MINUTES", 30))

    storage_endpoint: str = os.getenv(
        "STORAGE_ENDPOINT",
        "http://minio:9000"
    )

    storage_public_endpoint: str = os.getenv(
        "STORAGE_PUBLIC_ENDPOINT",
        "http://localhost:8080/files"
    )

    storage_access_key: str = os.getenv(
        "STORAGE_ACCESS_KEY",
        "minioadmin"
    )

    storage_secret_key: str = os.getenv(
        "STORAGE_SECRET_KEY",
        "minioadmin"
    )

    storage_region: str = os.getenv(
        "STORAGE_REGION",
        "us-east-1"
    )

    storage_upload_bucket: str = os.getenv(
        "STORAGE_UPLOAD_BUCKET",
        "uploads"
    )

    storage_converted_bucket: str = os.getenv(
        "STORAGE_CONVERTED_BUCKET",
        "converted"
    )

    app_name: str = os.getenv(
        "APP_NAME",
        "PixelForge API"
    )

    redis_url: str = os.getenv(
        "REDIS_URL",
        "redis://redis:6379"
    )

    celery_broker_url: AmqpDsn = os.getenv(
        "CELERY_BROKER_URL",
        "amqp://guest:guest@rabbitmq:5672//",
    )

    database_url: PostgresDsn = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@db/pixelforge",
    )

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

