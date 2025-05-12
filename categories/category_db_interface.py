from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from categories.models import Category


class CategoryDBInterface:
    async def fetch_all(self, session: AsyncSession, update_data: dict[str, Any]):
        category_query = select(Category).where(Category.name.in_(update_data["categories"]))
        category_result = await session.execute(category_query)
        return category_result.scalars().all()
