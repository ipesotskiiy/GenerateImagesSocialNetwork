import pytest

from communities.models import Community
from posts.models import Post


@pytest.mark.asyncio
async def test_create_community(authenticated_client, db_session):
    payload = {
        "name": "Test community",
        "description": "Test description"
    }

    response = await authenticated_client.post("/communities/create/", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert "community_id" in data

    community_in_db = await db_session.get(Community, data["community_id"])
    assert community_in_db is not None

    assert community_in_db.creator_id == authenticated_client.current_user.id


@pytest.mark.asyncio
async def test_get_all_communities(authenticated_client, db_session, first_community, second_community):
    response = await authenticated_client.get("/communities/all/")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 3


@pytest.mark.asyncio
async def test_get_community(authenticated_client, db_session, first_community):
    response = await authenticated_client.get(f"/communities/{first_community.id}/")
    assert response.status_code == 200

    data = response.json()
    assert first_community.name == data["name"]


@pytest.mark.asyncio
async def test_update_community(authenticated_client, db_session, first_community):
    payload = {"name": "Updated test first community"}
    description_before_change = first_community.description

    response = await authenticated_client.patch(f"/communities/update/{first_community.id}/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["description"] == description_before_change


@pytest.mark.asyncio
async def test_subscribe_to_community(authorize_second_user, db_session, first_community, second_user):
    response = await authorize_second_user.post(f"/communities/{first_community.id}/subscribe/")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "unsubscribed"

    response = await authorize_second_user.post(f"/communities/{first_community.id}/subscribe/")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "subscribed"


@pytest.mark.asyncio
async def test_create_post_in_community(authenticated_client, db_session, first_user, first_community, seed_categories):
    payload = {
        "title": "Test post in community",
        "content": "Test post in community content",
        "categories": [
            "Books"
        ],
        "user_id": first_user.id
    }

    response = await authenticated_client.post(f"/communities/{first_community.id}/posts/", json=payload)
    assert response.status_code == 201

    data = response.json()

    assert "post_id" in data

    post_in_db = await db_session.get(Post, data["post_id"])
    assert post_in_db is not None


@pytest.mark.asyncio
async def test_create_post_in_community(authenticated_client, db_session, first_user, first_community, seed_categories):
    payload = {
        "title": "Test post in community2",
        "content": "Test post in community content",
        "categories": [
            "Books"
        ],
        "user_id": first_user.id
    }

    response = await authenticated_client.post(f"/communities/{first_community.id}/posts/", json=payload)
    assert response.status_code == 201

    data = response.json()

    assert "post_id" in data

    post_in_db = await db_session.get(Post, data["post_id"])
    assert post_in_db is not None


@pytest.mark.asyncio
async def test_get_all_community_posts(
        authenticated_client,
        db_session,
        first_community,
        first_post_in_community,
        second_post_in_community):
    response = await authenticated_client.get(f"/communities/{first_community.id}/posts/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_community_post(
        authenticated_client,
        db_session,
        first_community,
        first_post_in_community):
    response = await authenticated_client.get(f"/communities/{first_community.id}/posts/{first_post_in_community.id}/")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "First test post in community"


@pytest.mark.asyncio
async def test_update_community_post(
        authenticated_client,
        db_session,
        first_community,
        second_post_in_community):

    payload = {"title": "Updated second test post in community"}

    response = await authenticated_client.patch(
        f"/communities/{first_community.id}/posts/{second_post_in_community.id}/",
        json=payload
    )
    assert response.status_code == 200

    data = response.json()
    post = await db_session.get(Post, data["post_id"])
    assert post.title == "Updated second test post in community"
    assert post.content == "Second test post in community content"

