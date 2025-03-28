import pytest

from auth.models import User


@pytest.mark.asyncio
async def test_register(async_client, db_session):
    payload = {
        "email": "test_user@mail.ru",
        "username": "test_user",
        "phone_number": "89298144303",
        "password": "hard_password",
        "first_name": "John",
        "last_name": "Doe",
        "date_of_birth": "2000-01-01",
        "bio": "Some biography text"
    }
    response = await async_client.post("/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert data["username"] == "test_user"
    assert "id" in data
    assert "password" not in data

    user_in_db = await db_session.get(User, data["id"])
    assert user_in_db is not None


@pytest.mark.asyncio
async def test_login(async_client):
    register_payload = {
        "email": "test_user1@mail.ru",
        "username": "test_user1",
        "phone_number": "89298144304",
        "password": "hard_password",
        "first_name": "John",
        "last_name": "Doe",
        "date_of_birth": "2000-01-01",
        "bio": "Some biography text"
    }
    reg_resp = await async_client.post("/auth/register", json=register_payload)
    assert reg_resp.status_code == 201

    login_data = {
        "username": "test_user1",
        "password": "hard_password"
    }
    resp = await async_client.post(
        "/auth/jwt/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert resp.status_code == 200, resp.text

    tokens = resp.json()
    assert "access_token" in tokens
    assert tokens["token_type"] == "bearer"

    assert len(tokens["access_token"]) > 0


@pytest.mark.asyncio
async def test_login_wrong_password(async_client):
    reg_resp = await async_client.post(
        "/auth/register",
        json={
            "email": "wrong_pwd_user@mail.ru",
            "username": "wrong_pwd_user",
            "phone_number": "89298144305",
            "password": "goodpassword",
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "2000-01-01",
            "bio": "Some biography text"
        }
    )
    assert reg_resp.status_code == 201

    resp = await async_client.post(
        "/auth/jwt/login",
        data={"username": "wrong_pwd_user", "password": "badpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert resp.status_code == 400, resp.text
    assert resp.json()["detail"] == "LOGIN_BAD_CREDENTIALS"
