"""Celery application bootstrap.

Provides a minimal Celery instance so the `celery_worker` service in
`docker-compose.yml` can start cleanly. Uses Redis for both broker and result
backend, matching the rest of the stack.
"""

from __future__ import annotations

from celery import Celery

from app.core.config import settings


def _create_celery() -> Celery:
    """Create and configure the Celery app."""
    app = Celery(
        "catholic_ride_share",
        broker=settings.REDIS_URL,
        backend=settings.REDIS_URL,
        include=["app.tasks.notifications"],
    )
    app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        enable_utc=True,
        timezone="UTC",
    )
    return app


celery_app = _create_celery()


@celery_app.task(name="health.ping")
def ping() -> str:
    """Lightweight health task for smoke tests."""
    return "pong"
