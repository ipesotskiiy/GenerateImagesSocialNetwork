from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from posts.models import Post
from posts.schemas import PostCreate, PostUpdate
from settings import get_async_session

router = APIRouter(
    prefix="/posts",
    tags=["Post"]
)


@router.get('/')
async def get_post(id: int, session: AsyncSession = Depends(get_async_session)):
    query = select(Post).where(Post.id == id)
    result = await session.execute(query)
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post_dict = {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "created_at": post.created_at,
        "user_id": post.user_id,
    }
    return post_dict


@router.get("/all")
async def get_all_posts(session: AsyncSession = Depends(get_async_session)):
    query = select(Post)
    result = await session.execute(query)
    posts = result.scalars().all()

    post_list = [
        {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "created_at": post.created_at,
            "user_id": post.user_id,
        }
        for post in posts
    ]

    return post_list


@router.post('/create')
async def add_post(new_post: PostCreate, session: AsyncSession = Depends(get_async_session)):
    stmt = insert(Post).values(**new_post.dict())
    await session.execute(stmt)
    await session.commit()
    return {"status": "Created"}


@router.patch("/update/{id}")
async def update_post(id: int, update_post: PostUpdate, session: AsyncSession = Depends(get_async_session)):
    query = select(Post).where(Post.id == id)
    result = await session.execute(query)
    existing_post = result.scalars().first()

    if not existing_post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Создаем словарь с полями, которые нужно обновить
    update_fields = {key: value for key, value in update_post.dict().items() if value is not None}

    # Проверяем, есть ли данные для обновления
    if not update_fields:
        raise HTTPException(status_code=400, detail="No data provided to update")

    stmt = (
        update(Post)
            .where(Post.id == id)
            .values(**update_fields)
            .execution_options(synchronize_session="fetch")
    )

    await session.execute(stmt)
    await session.commit()

    return {"status": "Updated"}


@router.delete("delete/{id}")
async def delete_post(id: int, session: AsyncSession = Depends(get_async_session)):
    query = select(Post).where(Post.id == id)
    result = await session.execute(query)
    existing_post = result.scalars().first()

    if not existing_post:
        raise HTTPException(status_code=404, detail="Post not found")

    stmt = delete(Post).where(Post.id == id)
    await session.execute(stmt)
    await session.commit()

    return {"status": "Deleted", "id": id}
