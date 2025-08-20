import pytest

from like_dislike.models import Like, Dislike


@pytest.mark.asyncio
async def test_like_new_post(
    authenticated_client,
    db_session,
    first_post,
):
    response = await authenticated_client.post(f"/likes/post/{first_post.id}/like")
    assert response.status_code == 200

    data = response.json()

    like_in_db = await db_session.get(Like, data["id"])
    assert like_in_db is not None
    assert like_in_db.content_id == first_post.id


@pytest.mark.asyncio
async def test_toggle_like_post(authenticated_client, db_session, first_post):
    response = await authenticated_client.post(f"/likes/post/{first_post.id}/like")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    like_id = data["id"]

    like_in_db = await db_session.get(Like, like_id)
    assert like_in_db is not None
    assert like_in_db.content_id == first_post.id

    response = await authenticated_client.post(f"/likes/post/{first_post.id}/like")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Лайк убран"

    like_in_db = await db_session.get(Like, like_id)
    assert like_in_db is None


@pytest.mark.asyncio
async def test_toggle_like_comment(authenticated_client, db_session, first_comment):
    comment_id = first_comment.id

    response = await authenticated_client.post(f"/likes/comment/{comment_id}/like")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    like_id = data["id"]

    like_in_db = await db_session.get(Like, like_id)
    assert like_in_db is not None
    assert like_in_db.content_id == comment_id
    assert like_in_db.content_type == "comment"

    response = await authenticated_client.post(f"/likes/comment/{comment_id}/like")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Лайк убран"

    like_in_db = await db_session.get(Like, like_id)
    assert like_in_db is None


@pytest.mark.asyncio
async def test_toggle_dislike_post(authenticated_client, db_session, first_post):
    response = await authenticated_client.post(f"/dislikes/post/{first_post.id}/dislike")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    dislike_id = data["id"]

    dislike_in_db = await db_session.get(Dislike, dislike_id)
    assert dislike_in_db is not None
    assert dislike_in_db.content_id == first_post.id

    response = await authenticated_client.post(f"/dislikes/post/{first_post.id}/dislike")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Дизлайк убран"

    dislike_in_db = await db_session.get(Dislike, dislike_id)
    assert dislike_in_db is None


@pytest.mark.asyncio
async def test_toggle_dislike_comment(authenticated_client, db_session, first_comment):
    comment_id = first_comment.id

    response = await authenticated_client.post(f"/dislikes/comment/{comment_id}/dislike")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    dislike_id = data["id"]

    dislike_in_db = await db_session.get(Dislike, dislike_id)
    assert dislike_in_db is not None
    assert dislike_in_db.content_id == comment_id
    assert dislike_in_db.content_type == "comment"

    response = await authenticated_client.post(f"/dislikes/comment/{comment_id}/dislike")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Дизлайк убран"

    dislike_in_db = await db_session.get(Dislike, dislike_id)
    assert dislike_in_db is None


@pytest.mark.asyncio
async def test_switch_like_to_dislike(authenticated_client, db_session, first_post):
    response = await authenticated_client.post(f"/likes/post/{first_post.id}/like")
    assert response.status_code == 200
    data = response.json()
    like_id = data.get("id")
    assert like_id is not None

    response = await authenticated_client.post(f"/dislikes/post/{first_post.id}/dislike")
    assert response.status_code == 200
    data = response.json()
    dislike_id = data.get("id")
    assert dislike_id is not None

    like_in_db = await db_session.get(Like, like_id)
    assert like_in_db is None

    dislike_in_db = await db_session.get(Dislike, dislike_id)
    assert dislike_in_db is not None


@pytest.mark.asyncio
async def test_switch_dislike_to_like(authenticated_client, db_session, first_post):
    response = await authenticated_client.post(f"/dislikes/post/{first_post.id}/dislike")
    assert response.status_code == 200
    data = response.json()
    dislike_id = data.get("id")
    assert dislike_id is not None

    response = await authenticated_client.post(f"/likes/post/{first_post.id}/like")
    assert response.status_code == 200
    data = response.json()
    like_id = data.get("id")
    assert like_id is not None

    dislike_in_db = await db_session.get(Dislike, dislike_id)
    assert dislike_in_db is None

    like_in_db = await db_session.get(Like, like_id)
    assert like_in_db is not None