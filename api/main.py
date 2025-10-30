import asyncio

from fastapi import FastAPI, APIRouter
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from routes.ws.utils import broadcast_listener

from core.db import (
    engine,
    Base,
)

from routes.job import router as job_router
from routes.user import router as user_router
from routes.auth import router as auth_router
from routes.format import router as format_router
from routes.ws.job import router as ws_job_router

from core.settings import get_settings
from core.storage import create_bucket_if_not_exists

settings = get_settings()

instrumentator = Instrumentator()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    asyncio.create_task(broadcast_listener())
    create_bucket_if_not_exists(settings.storage_upload_bucket)
    create_bucket_if_not_exists(settings.storage_converted_bucket)

    instrumentator.expose(app)

    yield


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
    swagger_ui_oauth2_redirect_url="/docs/oauth2-redirect",
)

instrumentator.instrument(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"]
)

app_router = APIRouter(prefix="/api/v1")

app_router.include_router(prefix="/job", router=job_router)
app_router.include_router(prefix="/auth", router=auth_router)
app_router.include_router(prefix="/user", router=user_router)
app_router.include_router(prefix="/format", router=format_router)
app_router.include_router(prefix="/ws", router=ws_job_router)

app.include_router(app_router)
