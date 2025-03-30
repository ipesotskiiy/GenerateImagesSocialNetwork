from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import User
from categories.models import Category
from communities.models import Community, CommunityMembership, CommunityRoleEnum
from communities.schemas import CreateCommunity, UpdateCommunity
from dependencies import current_user
from posts.models import Post
from posts.schemas import PostCreate, PostUpdate
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
async def create_community(
        data_for_new_community: CreateCommunity,
        current_user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session)
):
    community_data = data_for_new_community.dict()
    community_data["creator_id"] = current_user.id

    new_community = Community(**community_data)
    session.add(new_community)
    await session.flush()

    membership = CommunityMembership(
        user_id=current_user.id,
        community_id=new_community.id,
        role=CommunityRoleEnum.admin
    )
    session.add(membership)
    await session.commit()

    return {"status": "Created", "community_id": new_community.id}


@router.patch("/update/{community_id}/", summary="Обновить сообщество")
async def update_community(
        community_id: int,
        community_data: UpdateCommunity,
        current_user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    query = select(Community).where(Community.id == community_id)
    result = await session.execute(query)
    existing_community = result.scalars().first()

    if not existing_community:
        raise HTTPException(status_code=404, detail="Сообщество не найдено")

    if existing_community.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="У вас недостаточно прав для изменения этого сообщества")

    existing_community.name = community_data.name
    existing_community.description = community_data.description

    session.add(existing_community)

    await session.commit()
    await session.refresh(existing_community)

    return {"status": "Updated"}


@router.delete("/delete/{community_id}/", summary="Удалить сообщество")
async def delete_community(
        community_id: int,
        current_user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session)
):
    query = select(Community).where(Community.id == community_id)
    result = await session.execute(query)
    existing_community = result.scalars().first()

    if not existing_community:
        raise HTTPException(status_code=404, detail="Сообщество не найдено")

    if existing_community.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="У вас недостаточно прав для удаления этого сообщества")

    await session.delete(existing_community)
    await session.commit()

    return {"status": "Deleted", "id": community_id}


@router.post("/{community_id}/assign_moderator/{user_id}/", summary="Назначить модератора")
async def assign_moderator(
        community_id: int,
        user_id: int,
        current_user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session)
):
    # todo перенести работу с бд в отдельную дирректорию
    #######################
    query = select(CommunityMembership).where(
        CommunityMembership.community_id == community_id,
        CommunityMembership.user_id == current_user.id
    )

    result = await session.execute(query)
    #########################
    current_membership = result.scalars().first()

    if not current_membership or current_membership.role != CommunityRoleEnum.admin:
        raise HTTPException(status_code=403, detail="Нет прав для назначения модератора")

    query = select(CommunityMembership).where(
        CommunityMembership.community_id == community_id,
        CommunityMembership.user_id == user_id
    )
    result = await session.execute(query)
    membership = result.scalars().first()

    if not membership:
        raise HTTPException(status_code=404, detail="Пользователь не найден в сообществе")

    membership.role = CommunityRoleEnum.moderator
    session.add(membership)

    await session.commit()

    return {"status": "Role updated", "user_id": user_id, "role": membership.role.value}


@router.delete("/{community_id}/remove_user/{user_id}/", summary="Удалить участника из сообщества")
async def remove_user(
        community_id: int,
        user_id: int,
        current_user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session)
):
    query = select(CommunityMembership).where(
        CommunityMembership.community_id == community_id,
        CommunityMembership.user_id == current_user.id
    )
    result = await session.execute(query)
    current_membership = result.scalars().first()

    if not current_membership:
        raise HTTPException(status_code=403, detail="Вы не состоите в этом сообществе")

    query = select(CommunityMembership).where(
        CommunityMembership.community_id == community_id,
        CommunityMembership.user_id == user_id
    )
    result = await session.execute(query)
    target_membership = result.scalars().first()

    if not target_membership:
        raise HTTPException(status_code=404, detail="Пользователь не найден в сообществе")

    if current_membership.role == CommunityRoleEnum.moderator and target_membership.role != CommunityRoleEnum.user:
        raise HTTPException(status_code=403, detail="Модератор не может удалять администраторов или других модераторов")

    await session.delete(target_membership)
    await session.commit()

    return {"status": "User removed", "user_id": user_id}


@router.post("/{community_id}/subscribe/", summary="Подписаться/отписаться от сообщества")
async def toggle_subscription(
        community_id: int,
        current_user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session)
):
    query = select(Community).where(Community.id == community_id)
    result = await session.execute(query)
    community = result.scalars().first()

    if not community:
        raise HTTPException(status_code=404, detail="Сообщество не найдено")

    query = select(CommunityMembership).where(
        CommunityMembership.community_id == community_id,
        CommunityMembership.user_id == current_user.id
    )
    result = await session.execute(query)
    membership = result.scalars().first()

    if membership:
        await session.delete(membership)
        await session.commit()
        return {"status": "unsubscribed", "community_id": community_id}
    # TODO убрать else
    else:
        new_membership = CommunityMembership(
            user_id=current_user.id,
            community_id=community_id,
            role=CommunityRoleEnum.user
        )
        session.add(new_membership)
        await session.commit()
        return {"status": "subscribed", "community_id": community_id}


@router.post("/{community_id}/posts/", summary="Добавить пост в сообщество")
async def create_post_in_community(
        community_id: int,
        post_data: PostCreate,
        current_user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session)
):
    query = select(Community).where(Community.id == community_id)
    result = await session.execute(query)
    community = result.scalars().first()

    if not community:
        raise HTTPException(status_code=404, detail="Сообщество не найдено")

    query = select(CommunityMembership).where(
        CommunityMembership.community_id == community_id,
        CommunityMembership.user_id == current_user.id
    )
    result = await session.execute(query)
    membership = result.scalars().first()

    if not membership:
        raise HTTPException(status_code=403, detail="Вы не состоите в этом сообществе")

    if membership.role not in [CommunityRoleEnum.admin, CommunityRoleEnum.moderator]:
        raise HTTPException(status_code=403, detail="У вас нет прав для добавления постов в это сообщество")

    new_post = Post(
        title=post_data.title,
        content=post_data.content,
        user_id=current_user.id,
        community_id=community_id
    )
    try:
        categories_objects = []
        for cat_name in post_data.categories:
            result = await session.execute(select(Category).filter_by(name=cat_name))
            category_obj = result.scalar_one_or_none()
            categories_objects.append(category_obj)
    # TODO подоюрать конкретный Exception
    except Exception:
        raise HTTPException(status_code=404, detail="Не найденно данной категории")

    if not categories_objects:
        raise HTTPException(status_code=404, detail="Не найденно данной категории")
    new_post.categories = categories_objects

    session.add(new_post)
    await session.commit()
    await session.refresh(new_post)

    return {"status": "Post created", "post_id": new_post.id}


@router.get("/{community_id}/posts/", summary="Получить все посты в сообществе")
async def get_all_posts_in_community(
        community_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    query = select(Community).where(Community.id == community_id)
    result = await session.execute(query)
    community = result.scalars().first()

    if not community:
        raise HTTPException(status_code=404, detail="Сообщество не найдено")

    query = select(Post).where(Post.community_id == community_id).order_by(Post.created_at.desc())
    result = await session.execute(query)
    posts = result.scalars().all()

    return posts


@router.get("/{community_id}/posts/{post_id}/", summary="Получить пост по ID в сообществе")
async def get_post_in_community(
        community_id: int,
        post_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    query = select(Community).where(Community.id == community_id)
    result = await session.execute(query)
    community = result.scalars().first()

    if not community:
        raise HTTPException(status_code=404, detail="Сообщество не найдено")

    query = select(Post).where(
        Post.id == post_id,
        Post.community_id == community_id
    )
    result = await session.execute(query)
    post = result.scalars().first()

    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")

    return post


@router.patch("/{community_id}/posts/{post_id}/", summary="Обновить пост в сообществе")
async def update_post_in_community(
        community_id: int,
        post_id: int,
        post_update: PostUpdate,
        current_user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session)
):
    query = select(Community).where(Community.id == community_id)
    result = await session.execute(query)
    community = result.scalars().first()

    if not community:
        raise HTTPException(status_code=404, detail="Сообщество не найдено")

    query = select(CommunityMembership).where(
        CommunityMembership.community_id == community_id,
        CommunityMembership.user_id == current_user.id
    )
    result = await session.execute(query)
    membership = result.scalars().first()

    if not membership or membership.role not in [CommunityRoleEnum.admin, CommunityRoleEnum.moderator]:
        raise HTTPException(status_code=403, detail="Нет прав для обновления постов в этом сообществе")

    query = select(Post).where(
        Post.id == post_id,
        Post.community_id == community_id
    )
    result = await session.execute(query)
    post = result.scalars().first()

    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")

    # Обновляем поля поста, если они предоставлены
    if post_update.title is not None:
        post.title = post_update.title
    if post_update.content is not None:
        post.content = post_update.content

    session.add(post)
    await session.commit()
    await session.refresh(post)

    return {"status": "Post updated", "post_id": post.id}


@router.delete("/{community_id}/posts/{post_id}/", summary="Удалить пост в сообществе")
async def delete_post_in_community(
        community_id: int,
        post_id: int,
        current_user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session)
):
    # Проверяем существование сообщества
    query = select(Community).where(Community.id == community_id)
    result = await session.execute(query)
    community = result.scalars().first()

    if not community:
        raise HTTPException(status_code=404, detail="Сообщество не найдено")

    # Проверяем, что пользователь состоит в сообществе с правами admin или moderator
    query = select(CommunityMembership).where(
        CommunityMembership.community_id == community_id,
        CommunityMembership.user_id == current_user.id
    )
    result = await session.execute(query)
    membership = result.scalars().first()

    if not membership or membership.role not in [CommunityRoleEnum.admin, CommunityRoleEnum.moderator]:
        raise HTTPException(status_code=403, detail="Нет прав для удаления постов в этом сообществе")

    # Проверяем, что пост существует и принадлежит сообществу
    query = select(Post).where(
        Post.id == post_id,
        Post.community_id == community_id
    )
    result = await session.execute(query)
    post = result.scalars().first()

    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")

    await session.delete(post)
    await session.commit()

    return {"status": "Post deleted", "post_id": post_id}
