from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from communities.models import Community


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