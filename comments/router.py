from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, insert
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from auth.models import User
from comments.models import Comment
from comments.schemas import CommentCreate, CommentUpdate, CommentRead
from settings import get_async_session
from dependencies import current_user

router = APIRouter(
    prefix="/comments",
    tags=["Comments 💬"]
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

    # Обновление текста комментария
    existing_comment.text = comment_data.text

    # Сохранение изменений
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
