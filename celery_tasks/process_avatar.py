import os
from PIL import Image
from celery import shared_task
from sqlalchemy import update

from auth.models import User

from settings import sync_session


@shared_task(name="celery_tasks.process_avatar.process_avatar")
def process_avatar(user_id: int, input_path: str, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, f"{user_id}.jpg")

    with Image.open(input_path) as img:
        img = img.convert("RGB")
        img.thumbnail((300, 300))
        img.save(output_path, "JPEG")

    try:
        os.remove(input_path)
    except FileNotFoundError as e:
        print(f"Exception in avatar process: {e}")

    avatar_url = f"{output_path}"

    db = sync_session()
    db.execute(
        update(User).where(User.id==user_id).values(avatar_url=avatar_url)
    )
    db.commit()
    db.close()

    return avatar_url
