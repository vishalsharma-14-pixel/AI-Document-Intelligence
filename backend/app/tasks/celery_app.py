from celery import Celery

from app.config import settings

celery_app = Celery("docintel", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_track_started=True,
    broker_connection_retry_on_startup=True,
)

# app.tasks doesn't follow celery's autodiscover_tasks("<pkg>.tasks") convention
# (this IS the tasks package), so import task modules directly to register them.
from app.tasks import process_document  # noqa: E402,F401
