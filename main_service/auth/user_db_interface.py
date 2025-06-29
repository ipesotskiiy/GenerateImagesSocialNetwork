from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import UserGallery, User


class UserDBInterface:
    async def fetch_one(self, session: AsyncSession, photo_id: int, user_id: int):
        user_gallery = select(UserGallery).where(
            UserGallery.id == photo_id,
            UserGallery.user_id == user_id
        )
        photo = await session.execute(user_gallery)
        return photo.scalars().first()

    async def delete_one(self, session: AsyncSession, photo_id: int):
        await session.execute(delete(UserGallery).where(UserGallery.id == photo_id))
        await session.commit()


class UserInterface:
    async def fetch_one(self, session: AsyncSession, user_id:int):
        user = select(User).where(User.id == user_id)
        result = await session.execute(user)
        return result.scalars().first()