import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from core.db import (
    engine,
    Base,
)
from routes.job import router as job_router

from core.settings import get_settings

settings = get_settings()

os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.converted_dir, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app = FastAPI(title=settings.app_name)

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