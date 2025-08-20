import pytest

from comments.models import Comment


@pytest.mark.asyncio
async def test_create_comment(async_client, db_session, first_user, first_post):
    payload = {
        "text": "Test comment",
        "user_id": first_user.id,
        "post_id": first_post.id
    }

    response = await async_client.post("/comments/create/", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert 'id' in data

    comment_in_db = await db_session.get(Comment, data["id"])
    assert comment_in_db is not None


@pytest.mark.asyncio
async def test_get_all_comments(async_client, db_session, first_comment, second_comment):
    response = await async_client.get("/comments/all/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 1


@pytest.mark.asyncio
async def test_get_comment(async_client, db_session, first_comment):
    response = await async_client.get(f"/comments/{first_comment.id}/")
    assert response.status_code == 200
    data = response.json()
    assert data['text'] == "First test comment"


@pytest.mark.asyncio
async def test_update_comment(authenticated_client, db_session, first_comment):
    payload = {
        "text": "Updated first test comment text"
    }
    response = await authenticated_client.patch(f'/comments/update/{first_comment.id}/', json=payload)
    assert response.status_code == 200

    comment_data = response.json()
    assert 'id' in comment_data
    assert comment_data["text"] == "Updated first test comment text"



