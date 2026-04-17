"""Celery application configuration for SentinelGuard."""

import os
from celery import Celery

from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "sentinelguard",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.workers.tasks"]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Set up routing
celery_app.conf.task_routes = {
    "app.workers.tasks.log_request": {"queue": "logging"},
    "app.workers.tasks.cleanup_old_data": {"queue": "maintenance"},
    "app.workers.tasks.update_ip_reputation": {"queue": "analytics"},
}

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "cleanup-old-logs": {
        "task": "app.workers.tasks.cleanup_old_data",
        "schedule": 3600.0,  # Every hour
    },
    "update-reputations": {
        "task": "app.workers.tasks.update_ip_reputation",
        "schedule": 300.0,  # Every 5 minutes
    },
}

if __name__ == "__main__":
    celery_app.start()
