from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from categories.models import Category
from settings import get_async_session

# TODO Перенести константу в settings.py
DEFAULT_CATEGORIES = {
    "Music",
    "Books",
    "Movies",
    "Sport",
    "Travel",
    "Economy"
}


async def create_seed_categories(session: AsyncSession = Depends(get_async_session)):
    for cat_name in DEFAULT_CATEGORIES:
        result = await session.execute(select(Category).where(Category.name == cat_name))
        exists = result.scalars().first()
        if not exists:
            session.add(Category(name=cat_name))
    await session.commit()
