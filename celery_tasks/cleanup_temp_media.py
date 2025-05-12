import os

from celery import shared_task

from settings import get_settings


settings = get_settings()

@shared_task(name="celery_tasks.cleanup_temp_media")
def cleanup_temp_media():
    """
    Сканирует поддиректории MEDIA_URL,
    выбирает те, что оканчиваются на '_tmp',
    и удаляет из них все файлы.
    """
    deleted = []
    for name in os.listdir(settings.media_dir):
        if not name.endswith("_tmp"):
            continue

        tmp_dir = os.path.join(settings.media_dir, name)
        if not os.path.isdir(tmp_dir):
            continue

        for file_name in os.listdir(tmp_dir):
            file_path = os.path.join(tmp_dir, file_name)
            try:
                os.remove(file_path)
                deleted.append(file_path)
            except Exception as e:
                print(e)

    return {"deleted_count": len(deleted), "deleted_paths": deleted}
