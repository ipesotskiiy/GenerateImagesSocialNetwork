import pytest

from posts.models import Post


@pytest.mark.asyncio
async def test_create_post(async_client, db_session, first_user, seed_categories):
    payload = {
        "title": "Test post title",
        "content": "Test post description",
        "categories": ["Books"],
        "user_id": first_user.id
    }
    response = await async_client.post("/posts/create/", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert "id" in data

    post_in_db = await db_session.get(Post, data["id"])
    assert post_in_db is not None


@pytest.mark.asyncio
async def test_get_all_posts(async_client, first_post, second_post):
    response = await async_client.get("/posts/all/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 1


@pytest.mark.asyncio
async def test_get_post(async_client, first_post, second_post):
    response = await async_client.get(f"/posts/{second_post.id}/")
    assert response.status_code == 200
    print()
    print("RESPONSE TEXT:", response.text)
    print()
    data = response.json()
    assert data["title"] == "Test second post title"


@pytest.mark.asyncio
async def test_update_post(authorized_client_with_post):
    client, post = authorized_client_with_post

    response = await client.patch(
        f"/posts/update/{post.id}/",
        json={"title": "Изменённый заголовок"}
    )
    assert response.status_code == 200


