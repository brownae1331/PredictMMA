from celery import Celery

broker_url = "redis://redis:6379/0"
result_backend = "redis://redis:6379/1"

celery_app = Celery(
    "predictmma",
    broker=broker_url,
    backend=result_backend,
)
celery_app.autodiscover_tasks(packages=["app.tasks"])

# Optimized settings for high-volume task processing
celery_app.conf.task_acks_late = False  # Faster acknowledgments for bulk operations
celery_app.conf.worker_prefetch_multiplier = 8  # Prefetch more tasks to reduce round-trips
celery_app.conf.task_default_queue = "default"

# Connection and reliability settings
celery_app.conf.broker_heartbeat = 30  # Keep heartbeat for connection monitoring
celery_app.conf.broker_heartbeat_checkrate = 2  # Check heartbeat every 2x the heartbeat interval
celery_app.conf.worker_disable_rate_limits = True
celery_app.conf.task_time_limit = 600  # 10 minutes max per task
celery_app.conf.task_soft_time_limit = 540  # 9 minutes soft limit
celery_app.conf.worker_max_tasks_per_child = 1000  # Reduce restart overhead

# Performance optimizations for bulk operations
celery_app.conf.task_compression = 'gzip'  # Compress task payloads
celery_app.conf.result_compression = 'gzip'  # Compress results
# Use JSON for security (avoids root/pickle issues in Docker)
# If you need pickle performance and understand the security implications,
# uncomment the pickle lines below and add C_FORCE_ROOT=1 to worker environments
celery_app.conf.task_serializer = 'json'  # Secure serialization
celery_app.conf.result_serializer = 'json'
celery_app.conf.accept_content = ['json']  # Only accept JSON for security
# celery_app.conf.task_serializer = 'pickle'  # Faster but requires C_FORCE_ROOT=1
# celery_app.conf.result_serializer = 'pickle'
# celery_app.conf.accept_content = ['pickle', 'json']

# Redis connection pool settings
celery_app.conf.broker_connection_retry_on_startup = True
celery_app.conf.broker_pool_limit = 20  # Increase connection pool
celery_app.conf.result_backend_max_connections = 20

# Batching settings for chord/group operations
celery_app.conf.task_always_eager = False
celery_app.conf.task_eager_propagates = False
# Keep events enabled but optimize them
celery_app.conf.worker_send_task_events = True  # Required for Flower monitoring
celery_app.conf.task_send_sent_event = False  # Don't send task-sent events (not needed)
celery_app.conf.task_track_started = True  # Track when tasks start
celery_app.conf.event_queue_ttl = 300  # Event queue TTL (5 minutes)
celery_app.conf.event_queue_expires = 60.0  # Event expiration time

celery_app.conf.task_routes = {
    "import_fighter": {"queue": "scrape"},
    "scrape_event_fights": {"queue": "scrape"},
    "upsert_fight": {"queue": "db"},
    "import_event": {"queue": "db"},
    "import_rankings": {"queue": "db"},
    "sync_all_ufc_events": {"queue": "db"},
    "sync_recent_ufc_events": {"queue": "db"},
}