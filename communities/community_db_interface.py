from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from communities.models import Community, CommunityMembership


class CommunityDBInterface:
    async def fetch_all(self, session: AsyncSession):
        query = select(Community).order_by(Community.id)
        result = await session.execute(query)
        communities = result.scalars().all()
        return communities

    async def fetch_one(self, session: AsyncSession, community_id: int):
        query = select(Community).where(Community.id == community_id)
        result = await session.execute(query)
        community = result.scalars().first()
        return community


class CommunityMembershipDBInterface:
    async def fetch_one(self, session: AsyncSession, community_id: int, user_id: int):
        query = select(CommunityMembership).where(
            CommunityMembership.community_id == community_id,
            CommunityMembership.user_id == user_id
        )
        result = await session.execute(query)
        current_membership = result.scalars().first()
        return current_membership
