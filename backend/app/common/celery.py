from celery import Celery

celery_app = Celery(
    "predictmma",
    broker="redis://localhost:6379",
    backend="redis://localhost:6379",
)
celery_app.autodiscover_tasks(packages=["app.tasks"])
celery_app.conf.task_acks_late = True
celery_app.conf.worker_prefetch_multiplier = 1
celery_app.conf.task_default_queue = "default"
celery_app.conf.task_routes = {
    "tasks.imports.*": {"queue": "default"},
}