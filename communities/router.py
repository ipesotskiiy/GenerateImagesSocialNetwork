from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from communities.models import Community
from communities.schemas import CreateCommunity, UpdateCommunity
from settings import get_async_session

router = APIRouter(
    prefix="/communities",
    tags=["Communities 👪"]
)


@router.get("/all/", summary="Взять все сообщества")
async def get_all_communities(session: AsyncSession = Depends(get_async_session)):
    query = select(Community).order_by(Community.id)
    result = await session.execute(query)
    communities = result.scalars().all()

    return [
        {
            "id": community.id,
            "name": community.name,
            "description": community.description
        }
        for community in communities
    ]


@router.get("/{community_id}/", summary="Взять сообщество")
async def get_community(community_id: int, session: AsyncSession = Depends(get_async_session)):
    query = select(Community).where(Community.id == community_id)
    result = await session.execute(query)
    community = result.scalars().first()

    if not community:
        raise HTTPException(status_code=404, detail="Сообщество не найдено")

    return {
        "id": community.id,
        "name": community.name,
        "description": community.description
    }


@router.post("/create/", summary="Создать сообщество")
async def create_community(new_community: CreateCommunity, session: AsyncSession = Depends(get_async_session)):
    stmt = insert(Community).values(**new_community.dict())
    await session.execute(stmt)
    await session.commit()
    return {"status": "Created"}


@router.patch("/update/{community_id}/", summary="Обновить сообщество")
async def update_community(
        community_id: int,
        community_data: UpdateCommunity,
        session: AsyncSession = Depends(get_async_session),
):
    query = select(Community).where(Community.id == community_id)
    result = await session.execute(query)
    existing_community = result.scalars().first()

    if not existing_community:
        raise HTTPException(status_code=404, detail="Сообщество не найдено")

    existing_community.name = community_data.name
    existing_community.description = community_data.description

    session.add(existing_community)
    await session.commit()
    await session.refresh(existing_community)

    return {"status": "Updated"}


@router.delete("/delete/{community_id}/", summary="Удалить сообщество")
async def delete_community(
        community_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    query = select(Community).where(Community.id == community_id)
    result = await session.execute(query)
    existing_community = result.scalars().first()

    if not existing_community:
        raise HTTPException(status_code=404, detail="Сообщество не найдено")

    await session.delete(existing_community)
    await session.commit()
    return {"status": "Deleted", "id": community_id}
