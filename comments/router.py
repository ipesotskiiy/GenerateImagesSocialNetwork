import os
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import User
from celery_main import celery_app
from comments.db_interface import CommentsDBInterface, CommentImagesDBInterface
from comments.models import Comment, CommentImages
from comments.schemas import CommentCreate, CommentUpdate, CommentRead, CommentDelete
from settings import get_async_session, MEDIA_TEMP_COMMENT_IMAGES_URL, BASE_DIR
from dependencies import current_user

router = APIRouter(
    prefix="/comments",
    tags=["Comments 💬"]
)

router_comment_images = APIRouter(
    prefix="/comments_images",
    tags=["Comments Images 🌄"]
)

comment_db_interface = CommentsDBInterface()
comment_image_db_interface = CommentImagesDBInterface()

@router.get("/all/", response_model=List[CommentRead], summary="Взять все комментарии")
async def get_all_comments(session: AsyncSession = Depends(get_async_session)):
    comments = await comment_db_interface.fetch_all(session)
    return comments


@router.get('/{comment_id}/', response_model=CommentRead, summary="Взять комментарий")
async def get_comment(comment_id: int, session: AsyncSession = Depends(get_async_session)):
    comment = await comment_db_interface.fetch_one(session, comment_id)

    if not comment:
        raise HTTPException(status_code=404, detail="Коммент не найдена")

    return comment


@router.post('/create/', response_model=CommentRead, summary="Создать комментарий", status_code=201)
async def add_comment(new_comment: CommentCreate, session: AsyncSession = Depends(get_async_session)):
    comment = Comment(**new_comment.dict())
    session.add(comment)
    await session.commit()

    comment = await comment_db_interface.fetch_one(session, comment.id)
    return comment


@router.patch("/update/{comment_id}/", response_model=CommentRead, summary="Обновить комментарий")
async def update_comment(
        comment_id: int,
        comment_data: CommentUpdate,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(current_user)
):
    comment = await comment_db_interface.fetch_one(session, comment_id)

    if not comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден.")

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только автор может редактировать комментарий."
        )

    comment.text = comment_data.text

    session.add(comment)

    await session.commit()
    await session.refresh(comment)

    return comment


@router.delete("/delete/{comment_id}/", response_model=CommentDelete, summary="Удалить комментарий")
async def delete_comment(
        comment_id: int,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(current_user)
):
    comment = await comment_db_interface.fetch_one(session, comment_id)

    if not comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден")

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только автор можеть удалить комментарий."
        )

    await session.delete(comment)
    await session.commit()

    return {"status": "Deleted", "id": comment_id}

@router_comment_images.post(
    "/upload_images/{comment_id}/",
    summary="Прикрепить изображение к комментарию",
    status_code=status.HTTP_201_CREATED
)
async def upload_images(comment_id: int, files: list[UploadFile] = File(...)):
    os.makedirs(MEDIA_TEMP_COMMENT_IMAGES_URL, exist_ok=True)

    for file in files:
         tmp_name = f"{uuid.uuid4()}_{file.filename}"
         tmp_path = os.path.join(MEDIA_TEMP_COMMENT_IMAGES_URL, tmp_name)

         with open(tmp_path, "wb") as buf:
             buf.write(await file.read())

         celery_app.send_task(
             "celery_tasks.upload_comment_image.upload_comment_image",
             args=[comment_id, tmp_path]
         )
    return {"status": "processing", "count": len(files)}


@router_comment_images.delete(
    "/delete_images/{comment_id}/image/{image_id}/",
    summary="Удалить изображение с комментария",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_comment_images(
        comment_id: int,
        image_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    image = await comment_image_db_interface.fetch_one(session, comment_id, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    raw_paths = []
    if image.url:
        raw_paths.append(image.url)
    if image.thumbnail_url:
        raw_paths.append(image.thumbnail_url)

    await comment_image_db_interface.delete_one(session, image_id)

    for p in raw_paths:
        if os.path.isabs(p):
            full_path = p
        else:
            rel = p.lstrip("/")
            full_path = os.path.join(BASE_DIR, rel)
        celery_app.send_task(
            "celery_tasks.delete_comment_image",
            args=[full_path]
        )
    return
