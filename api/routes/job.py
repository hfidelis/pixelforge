import os
import uuid
import aiofiles

from celery import Celery
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status

from core.db import get_db
from core.settings import get_settings

from models.base import (
    Job,
    JobStatus,
)
from schemas.job import (
    JobCreate,
    JobRead,
    JobStatusRead,
)

settings = get_settings()

router = APIRouter()


@router.post(
    "/convert",
    response_model=JobRead,
)
async def create_job(
    schema: JobCreate = Depends(),
    db: AsyncSession = Depends(get_db),
) -> JobRead:
    if not schema.target_format:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="target_format required"
        )

    celery_client = Celery(broker=settings.celery_broker_url.unicode_string())

    ext = os.path.splitext(schema.file.filename)[1].lstrip(".").lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    input_path = os.path.join(settings.upload_dir, filename)

    contents = await schema.file.read()

    async with aiofiles.open(input_path, "wb") as out_file:
        await out_file.write(contents)

    job = Job(
        filename=schema.file.filename,
        input_path="/upload/" + filename,
        original_format=ext,
        target_format=schema.target_format,
        status=JobStatus.PENDING,
    )

    db.add(job)

    await db.commit()
    await db.refresh(job)

    celery_client.send_task(
        "convert_image",
        args=[job.id],
    )

    return job


@router.get(
    "/status/{job_id}",
    response_model=JobStatusRead,
)
async def get_status(
    job_id: int,
    db: AsyncSession = Depends(get_db)
) -> JobStatusRead:
    job = await db.get(Job, job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    return job


@router.get("/download/{job_id}")
async def download(
    job_id: int,
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    job = await db.get(Job, job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    if not job.output_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Output file not ready",
        )

    file_path = os.path.join(settings.converted_dir, os.path.basename(job.output_path))

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on disk",
        )

    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path)
    )

