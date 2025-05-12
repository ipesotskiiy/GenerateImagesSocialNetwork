from typing import List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import User
from categories.models import Category
from communities.community_db_interface import (
    CommunityDBInterface,
    CommunityMembershipDBInterface,
    CommunityPostDBInterface
)
from communities.models import (
    Community,
    CommunityMembership,
    CommunityRoleEnum
)
from communities.schemas import (
    CreateCommunity,
    UpdateCommunity,
    ReadCommunity,
    CommunityDelete,
    AssignModerator,
    RemoveUser,
    ToggleSubscription
)
from dependencies import current_user
from posts.models import Post
from posts.post_db_interface import PostDBInterface
from posts.schemas import (
    PostCreate,
    PostUpdate,
    PostRead,
    PostDelete
)
from settings import get_async_session

router = APIRouter(
    prefix="/communities",
    tags=["Communities 👪"]
)

community_db_interface = CommunityDBInterface()
community_membership_db_interface = CommunityMembershipDBInterface()
community_post_db_interface = CommunityPostDBInterface()
post_db_interface = PostDBInterface()

@router.get("/all/", response_model=List[ReadCommunity], summary="Взять все сообщества")
async def get_all_communities(session: AsyncSession = Depends(get_async_session)):
    communities = await community_db_interface.fetch_all(session)
    return communities

@router.get("/{community_id}/", response_model=ReadCommunity, summary="Взять сообщество")
async def get_community(community_id: int, session: AsyncSession = Depends(get_async_session)):
    community = await community_db_interface.fetch_one(session, community_id)

    if not community:
        raise HTTPException(status_code=404, detail="Сообщество не найдено")

    return community


@router.post("/create/", response_model=ReadCommunity, summary="Создать сообщество", status_code=201)
async def create_community(
    data_for_new_community: CreateCommunity,
    current_user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session)
):
    community_data = data_for_new_community.dict()
    community_data["creator_id"] = current_user.id

    new_community = Community(**community_data)
    session.add(new_community)
    await session.commit()
    await session.refresh(new_community)
    community_membership = CommunityMembership(user_id=current_user.id, community_id=new_community.id, role='admin')
    session.add(community_membership)
    await session.commit()
    await session.refresh(community_membership)

    return new_community


@router.patch("/update/{community_id}/", response_model=ReadCommunity, summary="Обновить сообщество")
async def update_community(
        community_id: int,
        community_data: UpdateCommunity,
        current_user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    existing_community = await community_db_interface.fetch_one(session, community_id)

    if not existing_community:
        raise HTTPException(status_code=404, detail="Сообщество не найдено")

    if existing_community.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="У вас недостаточно прав для изменения этого сообщества")

    if community_data.name:
        existing_community.name = community_data.name
    if community_data.description:
        existing_community.description = community_data.description

    session.add(existing_community)

    await session.commit()
    await session.refresh(existing_community)

    return existing_community


@router.delete("/delete/{community_id}/", response_model=CommunityDelete, summary="Удалить сообщество")
async def delete_community(
        community_id: int,
        current_user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session)
):
    existing_community = await community_db_interface.fetch_one(session, community_id)

    if not existing_community:
        raise HTTPException(status_code=404, detail="Сообщество не найдено")

    if existing_community.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="У вас недостаточно прав для удаления этого сообщества")

    await session.delete(existing_community)
    await session.commit()

    return {"status": "Deleted", "id": community_id}


@router.post(
    "/{community_id}/assign_moderator/{user_id}/",
    response_model=AssignModerator,
    summary="Назначить модератора"
)
async def assign_moderator(
    community_id: int,
    user_id: int,
    current_user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session)
):
    admin_membership = await community_membership_db_interface.fetch_one(
        session, community_id, current_user.id
    )
    if not admin_membership or admin_membership.role != CommunityRoleEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав для назначения модератора"
        )

    new_membership = await community_membership_db_interface.fetch_one(
        session, community_id, user_id
    )
    if not new_membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден в сообществе"
        )

    new_membership.role = CommunityRoleEnum.moderator

    session.add(new_membership)
    await session.commit()

    return {
        "status": "Role updated",
        "user_id": user_id,
        "role": new_membership.role.value
    }


@router.delete(
    "/{community_id}/remove_user/{user_id}/",
    response_model=RemoveUser,
    summary="Удалить участника из сообщества"
)
async def remove_user(
        community_id: int,
        user_id: int,
        current_user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session)
):

    current_membership = await community_membership_db_interface.fetch_one(session, community_id, current_user.id)

    if not current_membership:
        raise HTTPException(status_code=403, detail="Вы не состоите в этом сообществе")

    target_membership = await community_membership_db_interface.fetch_one(session, community_id, user_id)

    if not target_membership:
        raise HTTPException(status_code=404, detail="Пользователь не найден в сообществе")

    if current_membership.role == CommunityRoleEnum.moderator and target_membership.role != CommunityRoleEnum.user:
        raise HTTPException(status_code=403, detail="Модератор не может удалять администраторов или других модераторов")

    await session.delete(target_membership)
    await session.commit()

    return {"status": "User removed", "user_id": user_id}


@router.post(
    "/{community_id}/subscribe/",
    response_model=ToggleSubscription,
    summary="Подписаться/отписаться от сообщества"
)
async def toggle_subscription(
        community_id: int,
        current_user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session)
):

    community = await community_db_interface.fetch_one(session, community_id)

    if not community:
        raise HTTPException(status_code=404, detail="Сообщество не найдено")

    membership = await community_membership_db_interface.fetch_one(session, community_id, current_user.id)

    if membership:
        await session.delete(membership)
        await session.commit()
        return {"status": "unsubscribed", "community_id": community_id}

    new_membership = CommunityMembership(
        user_id=current_user.id,
        community_id=community_id,
        role=CommunityRoleEnum.user
    )
    session.add(new_membership)
    await session.commit()
    return {"status": "subscribed", "community_id": community_id}


@router.post("/{community_id}/posts/", response_model=PostRead, status_code=201, summary="Добавить пост в сообщество")
async def create_post_in_community(
        community_id: int,
        post_data: PostCreate,
        current_user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session)
):
    community = await community_db_interface.fetch_one(session, community_id)

    if not community:
        raise HTTPException(status_code=404, detail="Сообщество не найдено")

    membership = await community_membership_db_interface.fetch_one(session, community_id, current_user.id)

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
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Не найденно данной категории")

    if not categories_objects:
        raise HTTPException(status_code=404, detail="Не найденно данной категории")
    new_post.categories = categories_objects

    session.add(new_post)
    await session.commit()

    new_post = await post_db_interface.fetch_one(session, new_post.id)

    return new_post


@router.get("/{community_id}/posts/", response_model=List[PostRead], summary="Получить все посты в сообществе")
async def get_all_posts_in_community(
        community_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    community = community_db_interface.fetch_one(session, community_id)

    if not community:
        raise HTTPException(status_code=404, detail="Сообщество не найдено")

    posts = await community_post_db_interface.fetch_all(session, community_id)

    return posts


@router.get("/{community_id}/posts/{post_id}/", response_model=PostRead, summary="Получить пост по ID в сообществе")
async def get_post_in_community(
        community_id: int,
        post_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    community = await community_db_interface.fetch_one(session, community_id)

    if not community:
        raise HTTPException(status_code=404, detail="Сообщество не найдено")

    post = await community_post_db_interface.fetch_one(session, post_id, community_id)

    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")

    return post


@router.patch("/{community_id}/posts/{post_id}/", response_model=PostRead, summary="Обновить пост в сообществе")
async def update_post_in_community(
        community_id: int,
        post_id: int,
        post_update: PostUpdate,
        current_user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session)
):
    community = await community_db_interface.fetch_one(session, community_id)

    if not community:
        raise HTTPException(status_code=404, detail="Сообщество не найдено")

    membership = await community_membership_db_interface.fetch_one(session, community_id, current_user.id)

    if not membership or membership.role not in [CommunityRoleEnum.admin, CommunityRoleEnum.moderator]:
        raise HTTPException(status_code=403, detail="Нет прав для обновления постов в этом сообществе")

    post = await community_post_db_interface.fetch_one(session, post_id, community_id)

    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")

    if post_update.title is not None:
        post.title = post_update.title
    if post_update.content is not None:
        post.content = post_update.content

    session.add(post)
    await session.commit()
    updated_post = await community_post_db_interface.fetch_one(session, post_id, community_id)

    return updated_post


@router.delete("/{community_id}/posts/{post_id}/", response_model=PostDelete, summary="Удалить пост в сообществе")
async def delete_post_in_community(
        community_id: int,
        post_id: int,
        current_user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session)
):
    community = await community_db_interface.fetch_one(session, community_id)

    if not community:
        raise HTTPException(status_code=404, detail="Сообщество не найдено")

    membership = await community_membership_db_interface.fetch_one(session, community_id, current_user.id)

    if not membership or membership.role not in [CommunityRoleEnum.admin, CommunityRoleEnum.moderator]:
        raise HTTPException(status_code=403, detail="Нет прав для удаления постов в этом сообществе")

    post = await community_post_db_interface.fetch_one(session, post_id, community_id)

    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")

    await session.delete(post)
    await session.commit()

    return {"status": "Post deleted", "id": post_id}
