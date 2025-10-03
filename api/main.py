from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from core.db import (
    engine,
    Base,
)

from routes.job import router as job_router
from routes.auth import router as auth_router
from routes.user import router as user_router

from core.settings import get_settings
from core.storage import create_bucket_if_not_exists

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
    swagger_ui_oauth2_redirect_url="/auth/signin/form",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=[
        "Content-Type",
        "Authorization",
    ],
    allow_methods=[
        "GET",
        "POST",
        "HEAD",
        "OPTIONS",
    ]
)

app.include_router(
    prefix="/auth",
    tags=["auth"],
    router=auth_router,
)

app.include_router(
    prefix="/users",
    tags=["users"],
    router=user_router,
)

app.include_router(
    prefix="/jobs",
    tags=["jobs"],
    router=job_router,
)