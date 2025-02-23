from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import User
from comments.models import Comment
from like_dislike.models import Like
from like_dislike.schemas import LikeCreate, LikeResponse
from posts.models import Post
from settings import get_async_session
from dependencies import current_user

router = APIRouter(
    prefix="/likes",
    tags=["Likes ❤"]
)


async def toggle_like(like_data: LikeCreate, session: AsyncSession = Depends(get_async_session)):
    """
    Добавляет лайк, если его нет. Удаляет лайк, если он уже есть.
    """
    # Вместо session.query(Like).filter(...) делаем так:
    result = await session.execute(
        select(Like).where(
            Like.user_id == like_data.user_id,
            Like.content_id == like_data.content_id,
            Like.content_type == like_data.content_type
        )
    )
    existing_like = result.scalars().first()

    if existing_like:
        await session.delete(existing_like)
        await session.commit()
        return {
            "id": existing_like.id,
            "user_id": like_data.user_id,
            "content_id": like_data.content_id,
            "content_type": like_data.content_type
        }

    new_like = Like(**like_data.dict())
    session.add(new_like)
    await session.commit()
    await session.refresh(new_like)

    return new_like


@router.post("/post/{post_id}/like", summary="Поставить/убрать лайк на пост")
async def toggle_like_post(
        post_id: int,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(current_user),
):
    """
    Тоггл лайка поста:
    - Если лайка нет -> создаёт
    - Если лайк уже есть -> удаляет
    """
    post = await session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")

    like_data = LikeCreate(
        user_id=current_user.id,
        content_id=post_id,
        content_type="post"
    )

    result = await toggle_like(like_data, session)

    return result


@router.post("/comment/{comment_id}/like", summary="Поставить/убрать лайк на комментарий")
async def toggle_like_comment(
        comment_id: int,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(current_user),
):
    comment = await session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден")

    like_data = LikeCreate(
        user_id=current_user.id,
        content_id=comment_id,
        content_type="comment"
    )

    result = await toggle_like(like_data, session)

    return result
