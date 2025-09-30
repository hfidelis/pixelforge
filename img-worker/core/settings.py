import os

from dotenv import load_dotenv
from functools import lru_cache
from pydantic import PostgresDsn, AmqpDsn
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):

    app_name: str = os.getenv(
        "APP_NAME",
        "pixelforge-img-worker"
    )

    upload_dir: str = os.getenv(
        "UPLOAD_DIR",
        "/app/storage/upload",
    )

    converted_dir: str = os.getenv(
        "CONVERTED_DIR",
        "/app/storage/converted",
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
