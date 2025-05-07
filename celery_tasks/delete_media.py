import os

from celery import shared_task

from settings import settings


@shared_task(name="celery_tasks.delete_media")
def delete_media(path: str):
    if not os.path.isabs(path):
        path = os.path.join(settings.BASE_DIR, path)

    try:
        os.remove(path)
        return {"status": "deleted", "path": path}
    except FileNotFoundError:
        return {"status": "not_found", "path": path}
