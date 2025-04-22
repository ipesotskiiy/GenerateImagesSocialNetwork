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
celery_app.conf.update(result_expires=10000)
