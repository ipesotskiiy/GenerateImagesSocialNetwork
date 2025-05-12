from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from communities.models import Community, CommunityMembership
from posts.models import Post


class CommunityDBInterface:
    async def fetch_all(self, session: AsyncSession):
        query = select(Community).order_by(Community.id)
        result = await session.execute(query)
        return result.scalars().all()

    async def fetch_one(self, session: AsyncSession, community_id: int):
        query = select(Community).where(Community.id == community_id)
        result = await session.execute(query)
        return result.scalars().first()


class CommunityMembershipDBInterface:
    async def fetch_one(self, session: AsyncSession, community_id: int, user_id: int):
        query = select(CommunityMembership).where(
            CommunityMembership.community_id == community_id,
            CommunityMembership.user_id == user_id
        )
        result = await session.execute(query)
        return result.scalars().first()


class CommunityPostDBInterface:
    async def fetch_all(self, session: AsyncSession, community_id: int):
        query = select(Post).options(
                selectinload(Post.categories),
                selectinload(Post.likes),
                selectinload(Post.dislikes)
            ).where(Post.community_id == community_id).order_by(Post.created_at.desc())
        result = await session.execute(query)
        return result.scalars().all()

    async def fetch_one(self, session: AsyncSession, post_id, community_id):
        query = select(Post).options(
                selectinload(Post.categories),
                selectinload(Post.likes),
                selectinload(Post.dislikes)
            ).where(Post.id == post_id, Post.community_id == community_id)
        result = await session.execute(query)
        return result.scalars().first()

