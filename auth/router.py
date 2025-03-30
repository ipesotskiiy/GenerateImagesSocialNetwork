from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import current_user
from auth.models import User
from settings import get_async_session

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
