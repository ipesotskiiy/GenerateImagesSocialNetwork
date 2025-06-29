from typing import Union

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import User
from comments.models import Comment
from like_dislike.models import Like, Dislike
from like_dislike.reaction_db_interface import ReactionDBInterface
from like_dislike.schemas import LikeCreate, DislikeCreate, LikeResponse, DislikeResponse
from posts.models import Post
from settings import get_async_session
from dependencies import current_user

like_router = APIRouter(
    prefix="/likes",
    tags=["Likes ❤️"]
)

dislike_router = APIRouter(
    prefix="/dislikes",
    tags=["Dislikes 💔"]
)

reaction_db_interface = ReactionDBInterface()

async def toggle_reaction(reaction_data: Union[LikeResponse, DislikeResponse], session: AsyncSession = Depends(get_async_session)):
    """
    Универсальная функция для установки/снятия лайка или дизлайка.
    - Если реакция уже стоит, то она снимается.
    - Если реакции нет, то проверяется наличие противоположной реакции и, если она есть, удаляется,
      после чего создаётся новая реакция.
    """
    # Определяем, какая реакция передана, и выбираем соответствующую модель
    if reaction_data.__class__.__name__ == "LikeCreate":
        Model = Like
        OppositeModel = Dislike
        reaction_name = "лайк"
    else:
        Model = Dislike
        OppositeModel = Like
        reaction_name = 'дизлайк'

    existing_reaction = await reaction_db_interface.fetch_one(session, Model, reaction_data)

    existing_opposite = await reaction_db_interface.fetch_one(session, OppositeModel, reaction_data)

    if existing_reaction:
        # Если реакция уже стоит – снимаем её
        await session.delete(existing_reaction)
        await session.commit()
        return {"message": f"{reaction_name.capitalize()} убран", "id": existing_reaction.id}
    else:
        # Если противоположная реакция существует – удаляем её
        if existing_opposite:
            await session.delete(existing_opposite)
            await session.commit()
        # Добавляем новую реакцию
        new_reaction = Model(**reaction_data.dict())
        session.add(new_reaction)
        await session.commit()
        await session.refresh(new_reaction)
        return new_reaction


@like_router.post("/post/{post_id}/like", summary="Поставить/убрать лайк на пост")
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

    return await toggle_reaction(like_data, session)


@like_router.post("/comment/{comment_id}/like", summary="Поставить/убрать лайк на комментарий")
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

    return await toggle_reaction(like_data, session)


@dislike_router.post("/post/{post_id}/dislike", summary="Поставить/убрать дизлайк на пост")
async def toggle_dislike_post(
        post_id: int,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(current_user)
):
    """
    Тоггл дизлайка поста:
    - Если дизлайка нет -> создаёт
    - Если дизлайк уже есть -> удаляет
    """
    post = await session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")

    dislike_data = DislikeCreate(
        user_id=current_user.id,
        content_id=post_id,
        content_type="post"
    )

    return await toggle_reaction(dislike_data, session)


@dislike_router.post("/comment/{comment_id}/dislike", summary="Поставить/убрать дизлайк на комментарий")
async def toggle_dislike_comment(
        comment_id: int,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(current_user)
):
    comment = await session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден")

    dislike_data = DislikeCreate(
        user_id=current_user.id,
        content_id=comment_id,
        content_type="comment"
    )

    return await toggle_reaction(dislike_data, session)
