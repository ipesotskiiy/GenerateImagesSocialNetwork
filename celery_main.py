from celery import Celery

from settings import redis_url

print(redis_url)
celery_app = Celery(
    'celery_worker',
    broker=redis_url,
    backend=redis_url
)


from celery_tasks.process_avatar import process_avatar
from celery_tasks.process_gallery import process_gallery
from celery_tasks.delete_media import delete_media
from celery_tasks.upload_comment_image import upload_comment_image
from celery_tasks.delete_comment_image import delete_comment_image
from celery_tasks.upload_post_image import upload_post_image
from celery_tasks.delete_post_image import delete_post_image
celery_app.conf.update(result_expires=10000)
