from typing import Optional

from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from auth.models import User
from settings import get_async_session


class CustomUserDatabase(SQLAlchemyUserDatabase):

    async def get_by_username(self, username: str) -> Optional[User]:
        query = select(User).where(User.username == username)
        results = await self.session.execute(query)
        return results.scalars().first()


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield CustomUserDatabase(session, User)
