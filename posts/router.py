from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, insert
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import User
from posts.models import Post
from posts.schemas import PostCreate, PostUpdate
from settings import get_async_session
from dependencies import current_user

router = APIRouter(
    prefix="/posts",
    tags=["Posts 📖"]

)


@router.get('/{post_id}/', summary="Получить пост")
async def get_post(post_id: int, session: AsyncSession = Depends(get_async_session)):
    query = select(Post).where(Post.id == post_id)
    result: Result = await session.execute(query)
    post = result.scalars().first()

    if not post:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    post_dict = {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "created_at": post.created_at,
        "user_id": post.user_id,
    }
    return post_dict


@router.get("/all/", summary="Получить все посты")
async def get_all_posts(session: AsyncSession = Depends(get_async_session)):
    query = select(Post).order_by(Post.id)
    result: Result = await session.execute(query)
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


@router.post('/create/', summary="Создать пост")
async def add_post(new_post: PostCreate, session: AsyncSession = Depends(get_async_session)):
    stmt = insert(Post).values(**new_post.dict())
    await session.execute(stmt)
    await session.commit()
    return {"status": "Created"}


@router.patch("/update/{post_id}/", summary="Обновить пост")
async def update_post(
        post_id: int,
        post_data: PostUpdate,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(current_user)
):
    # Выполнение запроса
    query = select(Post).where(Post.id == post_id)
    result: Result = await session.execute(query)
    # Используем .scalars() для извлечения значений, а затем first()
    existing_post = result.scalars().first()
    if not existing_post:
        raise HTTPException(status_code=404, detail="Запись не найдена.")

    if existing_post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Только автор может редактировать пост."
        )

    # Формируем запрос на обновление
    existing_post.title = post_data.title
    existing_post.content = post_data.content

    # Выполнение запроса на обновление и коммит транзакции
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
