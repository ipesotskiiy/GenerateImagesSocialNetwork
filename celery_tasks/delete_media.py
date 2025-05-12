import os

from celery import shared_task

from settings import get_settings


settings = get_settings()

@shared_task(name="celery_tasks.delete_media")
def delete_media(path: str):
    if not os.path.isabs(path):
        path = os.path.join(settings.base_dir, path)

    try:
        os.remove(path)
        return {"status": "deleted", "path": path}
    except FileNotFoundError:
        return {"status": "not_found", "path": path}
