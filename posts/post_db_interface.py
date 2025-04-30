from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from posts.models import Post


class PostDBInterface:
    async def fetch_one(self, session: AsyncSession,  post_id: int):
        result = await session.execute(
            select(Post)
            .options(
                selectinload(Post.categories),
                selectinload(Post.likes),
                selectinload(Post.dislikes)
            )
            .where(Post.id == post_id)
        )
        new_post = result.scalars().first()
        return new_post
