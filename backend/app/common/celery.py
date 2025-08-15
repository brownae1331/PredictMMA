from celery import Celery
import os

broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery(
    "predictmma",
    broker=broker_url,
    backend=result_backend,
)
celery_app.autodiscover_tasks(packages=["app.tasks"])
celery_app.conf.task_acks_late = True
celery_app.conf.worker_prefetch_multiplier = 1
celery_app.conf.task_default_queue = "default"
celery_app.conf.task_routes = {
    "tasks.imports.*": {"queue": "default"},
}