from datetime import datetime
from typing import AsyncGenerator

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import (
    Column,
    Integer,
    String,
    TIMESTAMP
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from settings import Base, async_session_maker


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "Users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, unique=True)
    first_name = Column(String(25))
    last_name = Column(String(25))
    username = Column(String(40), index=True, unique=True, nullable=False)
    phone_number = Column(String(10))
    registered_at = Column(TIMESTAMP, default=datetime.utcnow)





async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)