import uuid
from io import BytesIO
from datetime import datetime, timezone
from PIL import Image
from main import celery
from core.db import SessionLocal
from models import Job, JobStatus
from core.settings import get_settings
from core.storage import storage_client

settings = get_settings()


@celery.task(name="convert_image", bind=True, acks_late=True)
def convert_image(self, job_id: int):
    session = SessionLocal()
    try:
        job = session.get(Job, job_id)
        if not job:
            self.update_state(state="FAILURE", meta={"reason": "job-not-found"})
            return

        job.status = JobStatus.PROCESSING
        job.started_at = datetime.now(timezone.utc)
        session.commit()

        response = storage_client.get_object(Bucket="uploads", Key=job.input_path)
        input_bytes = response['Body'].read()

        img = Image.open(BytesIO(input_bytes))
        target_ext = job.target_format
        out_buffer = BytesIO()

        if target_ext in ("jpg", "jpeg") and img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")

        img.save(out_buffer, format=target_ext.upper())
        out_buffer.seek(0)

        out_filename = f"{uuid.uuid4().hex}.{target_ext}"
        storage_client.put_object(
            Bucket=settings.storage_converted_bucket,
            Key=out_filename,
            Body=out_buffer,
            ContentType=f"image/{target_ext}"
        )

        job.output_path = out_filename
        job.status = JobStatus.SUCCESS
        job.finished_at = datetime.now(timezone.utc)

        session.commit()

        return {"output_path": out_filename}

    except Exception as exc:
        session.rollback()
        job.status = JobStatus.FAILED
        job.finished_at = datetime.now(timezone.utc)
        session.commit()
        raise
    finally:
        session.close()

