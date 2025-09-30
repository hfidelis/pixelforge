import os
from datetime import datetime, timezone
from PIL import Image
from main import celery
from core.db import SessionLocal
from models import Job, JobStatus
from core.settings import get_settings

settings = get_settings()


@celery.task(name="convert_image", bind=True, acks_late=True)
def convert_image(self, job_id: int):
    session = SessionLocal()

    try:
        print(f"Starting image conversion for job_id={job_id}")
        job = session.get(Job, job_id)

        if not job:
            self.update_state(state="FAILURE", meta={"reason": "job-not-found"})
            return

        job.status = JobStatus.PROCESSING
        job.started_at = datetime.now(timezone.utc)
        session.commit()

        rel_input = job.input_path.lstrip("/")
        if rel_input.startswith("upload/"):
            rel_input = rel_input[len("upload/"):]

        input_path = os.path.join(settings.upload_dir, rel_input)

        if not os.path.exists(input_path):
            raise FileNotFoundError(f"input file not found: {input_path}")

        base = os.path.splitext(os.path.basename(input_path))[0]
        target_ext = job.target_format.lstrip(".").lower()
        out_filename = f"{base}.{target_ext}"

        abs_output_path = os.path.join(settings.converted_dir, out_filename)
        os.makedirs(os.path.dirname(abs_output_path), exist_ok=True)

        with Image.open(input_path) as img:
            if target_ext in ("jpg", "jpeg") and img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")

            img.save(abs_output_path, format=target_ext.upper())

        rel_output_path = f"/converted/{out_filename}"

        job.output_path = rel_output_path
        job.status = JobStatus.SUCCESS
        job.finished_at = datetime.now(timezone.utc)
        session.commit()

        return {"output_path": abs_output_path}

    except Exception as exc:
        session.rollback()
        try:
            job = session.get(Job, job_id)
            if job:
                job.status = JobStatus.FAILED
                job.finished_at = datetime.now(timezone.utc)
                session.commit()
        except Exception:
            pass
        raise exc
    finally:
        session.close()
