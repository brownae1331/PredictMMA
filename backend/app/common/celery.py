from celery import Celery

broker_url = "redis://redis:6379/0"
result_backend = "redis://redis:6379/1"

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
    "import_fighter": {"queue": "scrape"},
    "scrape_event_fights": {"queue": "scrape"},
    "upsert_fight": {"queue": "db"},
    "import_event": {"queue": "db"},
    "import_rankings": {"queue": "db"},
    "sync_all_ufc_events": {"queue": "db"},
    "sync_recent_ufc_events": {"queue": "db"},
}