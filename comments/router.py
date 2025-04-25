import os
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy import select, insert, delete
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from auth.models import User
from celery_main import celery_app
from comments.models import Comment, CommentImages
from comments.schemas import CommentCreate, CommentUpdate, CommentRead
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


# TODO сделать return через pydantic


@router.get("/all/", response_model=List[CommentRead], summary="Взять все комментарии")
async def get_all_comments(session: AsyncSession = Depends(get_async_session)):
    query = select(Comment).options(
        selectinload(Comment.likes),
        selectinload(Comment.dislikes)
    ).order_by(Comment.id)
    result: Result = await session.execute(query)
    comments = result.scalars().all()

    return comments


@router.get('/{comment_id}/', response_model=CommentRead, summary="Взять комментарий")
async def get_comment(comment_id: int, session: AsyncSession = Depends(get_async_session)):
    query = select(Comment).options(
        selectinload(Comment.likes),
        selectinload(Comment.dislikes)
    ).where(Comment.id == comment_id)
    result: Result = await session.execute(query)
    comment = result.scalars().first()

    if not comment:
        raise HTTPException(status_code=404, detail="Коммент не найдена")

    return comment


@router.post('/create/', summary="Создать комментарий", status_code=201)
async def add_comment(new_comment: CommentCreate, session: AsyncSession = Depends(get_async_session)):
    stmt = insert(Comment).values(**new_comment.dict()).returning(Comment.id)

    result = await session.execute(stmt)
    await session.commit()

    created_id = result.scalar_one()
    return {"status": "Created", "id": created_id}


@router.patch("/update/{comment_id}/", summary="Обновить комментарий")
async def update_comment(
        comment_id: int,
        comment_data: CommentUpdate,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(current_user)
):
    query = select(Comment).where(Comment.id == comment_id)
    result: Result = await session.execute(query)
    existing_comment = result.scalars().first()

    if not existing_comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден.")

    if existing_comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только автор может редактировать комментарий."
        )

    existing_comment.text = comment_data.text

    session.add(existing_comment)

    await session.commit()
    await session.refresh(existing_comment)

    return {"status": "Updated", "comment_data": existing_comment}


@router.delete("/delete/{comment_id}/", summary="Удалить комментарий")
async def delete_comment(
        comment_id: int,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(current_user)
):
    query = select(Comment).where(Comment.id == comment_id)
    result: Result = await session.execute(query)
    existing_comment = result.scalars().first()

    if not existing_comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден")

    if existing_comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только автор можеть удалить комментарий."
        )

    await session.delete(existing_comment)
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
    result = await session.execute(
        select(CommentImages).where(
            CommentImages.id == image_id,
            CommentImages.comment_id == comment_id
        )
    )
    image = result.scalars().first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    raw_paths = []
    if image.url:
        raw_paths.append(image.url)
    if image.thumbnail_url:
        raw_paths.append(image.thumbnail_url)

    await session.execute(delete(CommentImages).where(CommentImages.id==image_id))
    await session.commit()

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
