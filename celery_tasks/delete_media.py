import os

from celery import shared_task

from settings import BASE_DIR


@shared_task(name="celery_tasks.delete_media")
def delete_media(path: str):
    # на всякий случай поправим относительный
    if not os.path.isabs(path):
        path = os.path.join(BASE_DIR, path)

    try:
        os.remove(path)
        return {"status": "deleted", "path": path}
    except FileNotFoundError:
        # файл уже удалён или неверный путь
        print(f"[delete_media] File not found: {path}")
        return {"status": "not_found", "path": path}
