from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from posts.models import Post


class PostDBInterface:
    async def fetch_one(self, session: AsyncSession,  post_id: int):
        post = await session.execute(
            select(Post)
            .options(
                selectinload(Post.categories),
                selectinload(Post.likes),
                selectinload(Post.dislikes)
            )
            .where(Post.id == post_id)
        )
        return post.scalars().first()

    async def fetch_all(self, session: AsyncSession):
        query = select(Post).options(
            selectinload(Post.categories),
            selectinload(Post.likes),
            selectinload(Post.dislikes)
        ).order_by(Post.id)
        result: Result = await session.execute(query)
        return result.scalars().all()