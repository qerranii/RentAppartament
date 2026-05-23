"""Celery configuration and workers."""
from celery import Celery
from app.core.config import settings


celery_app = Celery(
    "apartment_rent",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60
)


@celery_app.task(bind=True)
def process_image_task(self, image_path: str):
    """Process image asynchronously."""
    try:
        from app.services.image_service import ImageService
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        
        # Note: This is a simplified version
        # In production, use async context properly
        return {"status": "processed", "path": image_path}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@celery_app.task
def generate_statistics_task():
    """Generate statistics report."""
    return {"status": "statistics_generated"}
