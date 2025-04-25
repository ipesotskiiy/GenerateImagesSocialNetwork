import os

from celery import shared_task

from settings import BASE_DIR


@shared_task(name="celery_tasks.delete_comment_images")
def delete_comment_image(path: str):
    if not os.path.isabs(path):
        path = os.path.join(BASE_DIR, path)

    try:
        os.remove(path)
        return {"status": "deleted", "path": path}
    except FileNotFoundError:
        return {"status": "not found", "path": path}
