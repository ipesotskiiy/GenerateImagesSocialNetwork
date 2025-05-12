from celery import Celery
from celery.schedules import crontab

from settings import get_settings

settings = get_settings()

celery_app = Celery(
    'celery_worker',
    broker=settings.redis_url,
    backend=settings.redis_url
)


from celery_tasks.process_avatar import process_avatar
from celery_tasks.process_gallery import process_gallery
from celery_tasks.delete_media import delete_media
from celery_tasks.upload_comment_image import upload_comment_image
from celery_tasks.delete_comment_image import delete_comment_image
from celery_tasks.upload_post_image import upload_post_image
from celery_tasks.delete_post_image import delete_post_image
from celery_tasks.cleanup_temp_media import cleanup_temp_media

celery_app.conf.beat_schedule = {
    "cleanup-temp=media-at-midnight": {
        "task": "celery_tasks.cleanup_temp_media",
        "schedule": crontab(hour=0, minute=0)
    }
}

celery_app.conf.timezone = "Europe/Moscow"

celery_app.conf.update(
    result_expires=10000
)
