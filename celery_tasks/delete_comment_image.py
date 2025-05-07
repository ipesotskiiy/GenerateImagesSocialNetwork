import os.path

from celery import shared_task

from settings import settings


@shared_task(name="celery_tasks.delete_comment_image")
def delete_comment_image(path: str):
    if not os.path.isabs(path):
        path = os.path.join(settings.BASE_DIR, path)

    try:
        os.remove(path)
        return {"status": "deleted", "path": path}
    except FileNotFoundError:
        return {"status": "not_found", "path": path}
