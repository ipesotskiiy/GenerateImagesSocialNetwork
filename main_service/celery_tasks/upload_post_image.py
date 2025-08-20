import os

from PIL import Image
from celery import shared_task

from posts.models import PostImages
from settings import get_settings


settings = get_settings()

@shared_task(name="celery_tasks.upload_post_image.upload_post_image")
def upload_post_image(post_id: int, temp_path: str):
    os.makedirs(settings.media_post_images_dir, exist_ok=True)
    thumb_dir = os.path.join(settings.media_post_images_dir, "thumbnails")
    os.makedirs(thumb_dir, exist_ok=True)

    filename = os.path.basename(temp_path)
    final_path = os.path.join(settings.media_post_images_dir, filename)
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
        print(f"Exception in upload comment image process: {e}")

    db = sync_session()
    try:
        post_image = PostImages(
            post_id=post_id,
            url=f"/{final_path}",
            thumbnail_url=f"/{thumbnail_path}"
        )
        db.add(post_image)
        db.commit()

        db.refresh(post_image)

        result = {
            "id": post_image.id,
            "url": post_image.url,
            "thumbnail_url": post_image.thumbnail_url
        }
    finally:
        db.close()

    return result
