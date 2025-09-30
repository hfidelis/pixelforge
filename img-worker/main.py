from celery import Celery
from core.settings import get_settings

settings = get_settings()

celery = Celery(
    settings.app_name,
    broker=settings.broker_url.unicode_string(),
    include=["tasks"],
)

celery.conf.task_acks_late = True
celery.conf.worker_prefetch_multiplier = 1
