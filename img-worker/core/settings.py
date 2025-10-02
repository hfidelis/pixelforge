import os

from dotenv import load_dotenv
from functools import lru_cache
from pydantic import PostgresDsn, AmqpDsn
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    storage_endpoint: str = os.getenv(
        "STORAGE_ENDPOINT",
        "minio:9000"
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
        "pixelforge-img-worker"
    )

    broker_url: AmqpDsn = os.getenv(
        "BROKER_URL",
        "amqp://guest:guest@rabbitmq:5672//",
    )

    database_url: PostgresDsn = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@db/pixelforge",
    )

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
