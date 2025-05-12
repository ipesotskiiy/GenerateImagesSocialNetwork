import os
import shutil
import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    status
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.user_db_interface import UserDBInterface, UserInterface
from celery_main import celery_app
from dependencies import current_user
from auth.models import User
from settings import (
    get_async_session,
    get_settings
)

router = APIRouter(
    prefix="/subscriptions",
    tags=["Subscriptions 🔔"]
)

router_user_images = APIRouter(
    prefix="/media",
    tags=["User media 🖼️"]
)

user_db_interface = UserDBInterface()
user_interface = UserInterface()
settings = get_settings()

@router.post("/follow/{user_id}", summary="Подписаться/Отписаться от пользователя")
async def toggle_follow_user(
        user_id: int,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(current_user)
):
    await session.refresh(current_user, attribute_names=["following"])

    user_to_follow = await user_interface.fetch_one(session, user_id)

    if not user_to_follow:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user_to_follow in current_user.following:
        current_user.following.remove(user_to_follow)
        await session.commit()
        return {"message": f"Вы успешно отписались от {user_to_follow.username}"}
    current_user.following.append(user_to_follow)
    await session.commit()
    return {"message": f"Вы успешно подписались на {user_to_follow.username}"}


@router_user_images.post("/user/{user_id}/avatar/", summary="Установить пользователю аватар")
async def upload_avatar(user_id: int, file: UploadFile = File(...)):
    temp_path = f"{settings.media_temp_avatar_dir}/{uuid.uuid4()}_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    celery_app.send_task(
        "celery_tasks.process_avatar.process_avatar",
        args=[user_id, temp_path, settings.media_avatar_dir]
    )
    return {"status": "processing"}


@router_user_images.post("/users/{user_id}/photos/", summary="Добавить фотаграфии", status_code=status.HTTP_201_CREATED)
async def upload_photos(user_id: int, files: list[UploadFile] = File(...)):
    os.makedirs(settings.media_temp_user_photos_dir, exist_ok=True)

    for file in files:
        tmp_name = f"{uuid.uuid4()}_{file.filename}"
        tmp_path = os.path.join(settings.media_temp_user_photos_dir, tmp_name)

        # Сохраняем во временное хранилище
        with open(tmp_path, "wb") as buf:
            buf.write(await file.read())

        celery_app.send_task(
            "celery_tasks.process_gallery.process_gallery",
            args=[user_id, tmp_path]
        )

    return {"status": "processing", "count": len(files)}


@router_user_images.delete(
    "/users/{user_id}/photo/{photo_id}/",
    summary="Удалить фотографию",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_photos(
    user_id: int,
    photo_id: int,
    session: AsyncSession = Depends(get_async_session)
):

    photo = await user_db_interface.fetch_one(session, photo_id, user_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    raw_paths = []
    if photo.url:
        raw_paths.append(photo.url)
    if photo.thumbnail_url:
        raw_paths.append(photo.thumbnail_url)

    await user_db_interface.delete_one(session, photo_id)

    for p in raw_paths:
        if os.path.isabs(p):
            full_path = p
        else:
            rel = p.lstrip("/")
            full_path = os.path.join(settings.base_dir, rel)
        celery_app.send_task(
            "celery_tasks.delete_media.delete_media",
            args=[full_path]
        )

    return

