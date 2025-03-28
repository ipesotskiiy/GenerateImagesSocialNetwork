from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from auth.models import User
from categories.models import Category
from posts.models import Post
from posts.schemas import PostCreate, PostUpdate, PostRead
from settings import get_async_session
from dependencies import current_user

router = APIRouter(
    prefix="/posts",
    tags=["Posts 📖"]

)


@router.get("/all/", response_model=List[PostRead], summary="Получить все посты")
async def get_all_posts(session: AsyncSession = Depends(get_async_session)):
    query = select(Post).options(
        selectinload(Post.categories),
        selectinload(Post.likes),
        selectinload(Post.dislikes)
    ).order_by(Post.id)
    result: Result = await session.execute(query)
    posts = result.scalars().all()
    return posts


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


@router.post('/create/', summary="Создать пост", status_code=201)
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


@router.patch("/update/{post_id}/", summary="Обновить пост")
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
