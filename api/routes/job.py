import uuid

from celery import Celery
from sqlalchemy import select
from datetime import timedelta
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status, Request

from core.db import get_db
from utils.pagination import paginate
from core.settings import get_settings
from core.storage import storage_client
from utils.dependencies import get_current_user

from models.job import (
    Job,
    JobStatus,
)

from schemas.job import (
    JobCreate,
    JobRead,
    JobStatusRead,
    JobImageExtension,
    PresignedRedirectResponse,
)

from schemas.pagination import (
    PaginationParams,
    PaginatedResponse,
)

settings = get_settings()

router = APIRouter(tags=["jobs"])

@router.get(
    "/",
    response_model=PaginatedResponse[JobRead],
)
async def list_jobs(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
    pagination: PaginationParams = Depends(),
) -> PaginatedResponse[JobRead]:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    query = select(Job).where(Job.user_id == user.id).order_by(Job.id.desc())

    result = await paginate(
        db=db,
        model=Job,
        base_query=query,
        page=pagination.page,
        size=pagination.size,
        request=request,
    )


    return result

@router.post(
    "/convert",
    response_model=JobRead,
)
async def create_job(
    schema: JobCreate = Depends(),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> JobRead:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    if not schema.target_format:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="target_format required"
        )

    ext = schema.file.filename.split(".")[-1].lower()

    if not JobImageExtension.has_value(ext):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported input file format, supported formats: {', '.join(JobImageExtension.list_values())}"
        )

    filename = f"{uuid.uuid4().hex}.{ext}"
    celery_client = Celery(broker=settings.celery_broker_url.unicode_string())

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
        user_id=user.id,
        target_format=schema.target_format.value,
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
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> JobStatusRead:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    job = await db.get(Job, job_id)

    if not job or job.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    return job


@router.get("/download/{job_id}")
async def download(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> StreamingResponse:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    job = await db.get(Job, job_id)

    if not job or job.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    if not job.output_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Output file not ready",
        )

    storage_signed_url = storage_client.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": settings.storage_converted_bucket,
            "Key": job.output_path,
        },
        ExpiresIn=timedelta(minutes=15).total_seconds(),
    )

    filename = f"{job.filename.split('.')[0]}.{job.target_format}"

    return PresignedRedirectResponse(
        url=storage_signed_url,
        filename=filename,
    )

