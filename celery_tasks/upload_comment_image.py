import os

from PIL import Image
from celery import shared_task

from comments.models import CommentImages
from settings import settings, sync_session


@shared_task(name="celery_tasks.upload_comment_image.upload_comment_image")
def upload_comment_image(comment_id: int, temp_path: str):
    os.makedirs(settings.media_comment_images_dir, exist_ok=True)
    thumb_dir = os.path.join(settings.media_comment_images_dir, "thumbnails")
    os.makedirs(thumb_dir, exist_ok=True)

    filename = os.path.basename(temp_path)
    final_path = os.path.join(settings.media_comment_images_dir, filename)
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
        comment_image = CommentImages(
            comment_id=comment_id,
            url=f"/{final_path}",
            thumbnail_url=f"/{thumbnail_path}"
        )
        db.add(comment_image)
        db.commit()

        db.refresh(comment_image)

        result= {
            "id": comment_image.id,
            "url": comment_image.url,
            "thumbnail_url": comment_image.thumbnail_url
        }
    finally:
        db.close()

    return result


