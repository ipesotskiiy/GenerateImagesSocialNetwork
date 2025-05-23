import os

from PIL import Image
from celery import shared_task

from auth.models import UserGallery
from settings import get_settings, get_sync_engine

settings = get_settings()

@shared_task(name="celery_tasks.process_gallery.process_gallery")
def process_gallery(user_id: int, temp_path: str):
    os.makedirs(settings.media_user_photos_dir, exist_ok=True)
    thumb_dir = os.path.join(settings.media_user_photos_dir, "thumbnails")
    os.makedirs(thumb_dir, exist_ok=True)

    filename = os.path.basename(temp_path)
    final_path = os.path.join(settings.media_user_photos_dir, filename)
    thumbnail_path = os.path.join(thumb_dir, filename)

    with Image.open(temp_path) as img:
        img = img.convert("RGB")
        img.save(final_path, "JPEG", optimize=True)

    with Image.open(temp_path) as img:
        img = img.convert("RGB")
        img.thumbnail((150, 150))
        img.save(thumbnail_path, "JPEG", optimize=True)


    try:
        os.remove(temp_path)
    except FileNotFoundError as e:
        print(f"Exception in gallery process: {e}")

    db = get_sync_engine()
    try:
        gallery_item = UserGallery(
            user_id=user_id,
            url=f"/{final_path}",
            thumbnail_url=f"/{thumbnail_path}"
        )
        db.add(gallery_item)
        db.commit()

        db.refresh(gallery_item)

        result = {
            "id": gallery_item.id,
            "url": gallery_item.url,
            "thumbnail_url": gallery_item.thumbnail_url
        }
    finally:
        db.close()

    return result
