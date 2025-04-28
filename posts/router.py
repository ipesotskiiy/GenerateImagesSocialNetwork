import os
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy import select, delete
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from auth.models import User
from categories.models import Category
from celery_main import celery_app
from posts.models import Post, PostImages
from posts.schemas import PostCreate, PostUpdate, PostRead
from settings import get_async_session, MEDIA_TEMP_POST_IMAGES_URL, BASE_DIR
from dependencies import current_user

router = APIRouter(
    prefix="/posts",
    tags=["Posts 📖"]

)

router_post_images = APIRouter(
    prefix="/posts_images",
    tags=["Posts Images 📸"]
)


@router.get("/all/", response_model=List[PostRead], summary="Получить все посты")
async def get_all_posts(session: AsyncSession = Depends(get_async_session)):
    query = select(Post).options(
        selectinload(Post.categories),
        selectinload(Post.likes),
        selectinload(Post.dislikes)
    ).order_by(Post.id)
    result: Result = await session.execute(query)

    return result.scalars().all()


@router.get('/{post_id}/', response_model=PostRead, summary="Получить пост")
async def get_post(post_id: int, session: AsyncSession = Depends(get_async_session)):
    query = select(Post).where(Post.id == post_id).options(
        selectinload(Post.categories),
        selectinload(Post.likes),
        selectinload(Post.dislikes)
    )
    result: Result = await session.execute(query)

    post = result.scalars().first()

    if not post:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    return post


@router.post('/create/', response_model=PostRead, summary="Создать пост", status_code=201)
async def add_post(new_post: PostCreate, session: AsyncSession = Depends(get_async_session)):
    post_data = new_post.dict(exclude={"categories"})
    post = Post(**post_data)

    categories_objects = []

    for cat_name in new_post.categories:
        result = await session.execute(select(Category).filter_by(name=cat_name))
        category_obj = result.scalar_one_or_none()

        categories_objects.append(category_obj)

    post.categories = categories_objects

    session.add(post)
    await session.commit()
    await session.refresh(post)

    return {"status": "Created", "id": post.id}


@router.patch("/update/{post_id}/", response_model=PostRead, summary="Обновить пост")
async def update_post(
        post_id: int,
        post_data: PostUpdate,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(current_user)
):
    query = select(Post).where(Post.id == post_id).options(selectinload(Post.categories))
    result: Result = await session.execute(query)
    existing_post = result.scalars().first()

    if not existing_post:
        raise HTTPException(status_code=404, detail="Запись не найдена.")

    if existing_post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Только автор может редактировать пост."
        )

    update_data = post_data.model_dump(exclude_unset=True)

    if "title" in update_data:
        existing_post.title = update_data["title"]

    if "content" in update_data:
        existing_post.content = update_data["content"]

    if "categories" in update_data:
        category_query = select(Category).where(Category.name.in_(update_data["categories"]))
        category_result = await session.execute(category_query)
        categories = category_result.scalars().all()
        existing_post.categories = categories

    session.add(existing_post)
    await session.commit()
    await session.refresh(existing_post)

    return {"status": "Updated"}


@router.delete("/delete/{post_id}/", summary="Удалить пост 💣")
async def delete_post(
        post_id: int,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(current_user)
):
    query = select(Post).where(Post.id == post_id)
    result: Result = await session.execute(query)
    existing_post = result.scalars().first()

    if not existing_post:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    if existing_post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только автор может удалить пост"
        )

    await session.delete(existing_post)
    await session.commit()

    return {"status": "Deleted", "id": post_id}


@router_post_images.post(
    "/upload_images/{post_id}/",
    summary="Прикрепить изображение к посту",
    status_code=status.HTTP_201_CREATED
)
async def upload_images(post_id: int, files: list[UploadFile] = File(...)):
    os.makedirs(MEDIA_TEMP_POST_IMAGES_URL, exist_ok=True)

    for file in files:
        tmp_name = f"{uuid.uuid4()}_{file.filename}"
        tmp_path = os.path.join(MEDIA_TEMP_POST_IMAGES_URL, tmp_name)

        with open(tmp_path, "wb") as buf:
            buf.write(await file.read())

        celery_app.send_task(
            "celery_tasks.upload_post_image.upload_post_image",
            args=[post_id, tmp_path]
        )
    return {"status": "processing", "count": len(files)}


@router_post_images.delete(
    "/delete_images/{post_id}/image/{image_id}",
    summary="Удалить изображение с поста",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_post_images(
        post_id: int,
        image_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(
        select(PostImages).where(
            PostImages.id == image_id,
            PostImages.post_id == post_id
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

    await session.execute(delete(PostImages).where(PostImages.id==image_id))
    await session.commit()

    for p in raw_paths:
        if os.path.isabs(p):
            full_path = p
        else:
            rel = p.lstrip("/")
            full_path = os.path.join(BASE_DIR, rel)
        celery_app.send_task(
                "celery_tasks.delete_post_image",
                args=[full_path]
            )
    return

