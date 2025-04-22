import os
import shutil
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from celery_main import celery_app
from celery_tasks import process_avatar, process_gallery
from dependencies import current_user
from auth.models import User
from settings import get_async_session, MEDIA_TEMP_AVATAR_URL, MEDIA_AVATAR_URL, MEDIA_TEMP_USER_PHOTOS_URL

router = APIRouter(
    prefix="/subscriptions",
    tags=["Subscriptions 🔔"]
)


@router.post("/follow/{user_id}", summary="Подписаться/Отписаться от пользователя")
async def toggle_follow_user(
        user_id: int,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(current_user)
):
    await session.refresh(current_user, attribute_names=["following"])

    # TODO переименовать переменную
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user_to_follow = result.scalars().first()

    if not user_to_follow:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user_to_follow in current_user.following:
        current_user.following.remove(user_to_follow)
        await session.commit()
        return {"message": f"Вы успешно отписались от {user_to_follow.username}"}
    # TODO убрать else
    else:
        current_user.following.append(user_to_follow)
        await session.commit()
        return {"message": f"Вы успешно подписались на {user_to_follow.username}"}


@router.post("/user/{user_id}/avatar/", summary="Установить пользователю аватар")
async def upload_avatar(user_id: int, file: UploadFile = File(...)):
    temp_path = f"{MEDIA_TEMP_AVATAR_URL}/{uuid.uuid4()}_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    celery_app.send_task(
        "celery_tasks.process_avatar.process_avatar",
        args=[user_id, temp_path, MEDIA_AVATAR_URL]
    )
    return {"status": "processing"}


@router.post("/users/{user_id}/photos/")
async def upload_photos(user_id: int, files: list[UploadFile] = File(...)):
    os.makedirs(MEDIA_TEMP_USER_PHOTOS_URL, exist_ok=True)

    for file in files:
        tmp_name = f"{uuid.uuid4()}_{file.filename}"
        tmp_path = os.path.join(MEDIA_TEMP_USER_PHOTOS_URL, tmp_name)

        # Сохраняем во временное хранилище
        with open(tmp_path, "wb") as buf:
            buf.write(await file.read())

        celery_app.send_task(
            "celery_tasks.process_gallery.process_gallery",
            args=[user_id, tmp_path]
        )

    return {"status": "processing", "count": len(files)}

