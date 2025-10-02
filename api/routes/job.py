import os
import uuid

from celery import Celery
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status

from core.db import get_db
from core.settings import get_settings
from core.storage import storage_client

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

    ext = schema.file.filename.split(".")[-1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"

    contents = await schema.file.read()

    storage_client.put_object(
        Bucket=settings.storage_upload_bucket,
        Key=filename,
        Body=contents,
        ContentType=schema.file.content_type,
    )

    job = Job(
        filename=schema.file.filename,
        input_path=filename,
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
) -> StreamingResponse:
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

    obj = storage_client.get_object(
        Bucket=settings.storage_converted_bucket,
        Key=job.output_path,
    )

    return StreamingResponse(
        obj['Body'],
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={job.filename}"
        }
    )

