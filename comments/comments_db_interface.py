from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from comments.models import Comment, CommentImages


class CommentsDBInterface:
    def build_select(self):
        return (
            select(Comment).options(
                selectinload(Comment.likes),
                selectinload(Comment.dislikes)
            )
        )

    async def fetch_all(self, session: AsyncSession):
        comments = self.build_select().order_by(Comment.id)
        result = await session.execute(comments)
        return result.scalars().all()

    async def fetch_one(self, session: AsyncSession, comment_id: int):
        comment = self.build_select().where(Comment.id == comment_id)
        result = await session.execute(comment)
        return result.scalar_one_or_none()

class CommentImagesDBInterface:
    async def fetch_one(self, session: AsyncSession, comment_id: int, image_id: int):
        result = await session.execute(
            select(CommentImages).where(
                CommentImages.id == image_id,
                CommentImages.comment_id == comment_id
            )
        )
        image = result.scalars().first()
        return image

    async def delete_one(self, session: AsyncSession, image_id: int):
        await session.execute(delete(CommentImages).where(CommentImages.id == image_id))
        await session.commit()

