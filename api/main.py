from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from core.db import (
    engine,
    Base,
)
from core.storage import create_bucket_if_not_exists
from routes.job import router as job_router

from core.settings import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    create_bucket_if_not_exists(settings.storage_upload_bucket)
    create_bucket_if_not_exists(settings.storage_converted_bucket)

    yield


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"],
)

app.include_router(
    prefix="/jobs",
    tags=["jobs"],
    router=job_router,
)