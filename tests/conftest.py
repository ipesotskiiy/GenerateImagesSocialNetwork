import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from httpx import AsyncClient, ASGITransport

from auth.models import User
from categories.models import Category
from comments.models import Comment
from communities.models import Community
from main import app
from posts.models import Post
from settings import get_async_session, Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

async_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    future=True
)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    autoflush=False
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest_asyncio.fixture
async def db_session():
    async with AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def async_client(db_session):
    def override_get_async_session():
        yield db_session

    app.dependency_overrides[get_async_session] = override_get_async_session

    transport = ASGITransport(app=app, raise_app_exceptions=True)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def first_user(async_client, db_session):
    payload = {
        "email": "first_test_user@mail.ru",
        "username": "first_test_user",
        "phone_number": "89298144301",
        "password": "hard_password",
        "first_name": "John",
        "last_name": "Doe",
        "date_of_birth": "2000-01-01",
        "bio": "Some biography text"
    }
    response = await async_client.post("/auth/register", json=payload)
    assert response.status_code == 201

    data = response.json()
    user_in_db = await db_session.get(User, data["id"])

    await db_session.refresh(user_in_db)
    assert user_in_db is not None
    yield user_in_db

    await db_session.delete(user_in_db)
    await db_session.commit()


@pytest_asyncio.fixture
async def authorize_first_user(async_client, db_session, first_user):
    login_data = {
        "username": first_user.username,
        "password": "hard_password"
    }

    login_resp = await async_client.post(
        "/auth/jwt/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert login_resp.status_code == 200

    access_token = login_resp.json()["access_token"]

    async_client.headers.update({
        "Authorization": f"Bearer {access_token}"
    })

    async_client.current_user = first_user

    return async_client


@pytest_asyncio.fixture
async def second_user(async_client, db_session):
    payload = {
        "email": "second_test_user@mail.ru",
        "username": "second_test_user",
        "phone_number": "89298144302",
        "password": "hard_password",
        "first_name": "John",
        "last_name": "Doe",
        "date_of_birth": "2000-01-01",
        "bio": "Some biography text"
    }
    response = await async_client.post("/auth/register", json=payload)
    assert response.status_code == 201

    data = response.json()
    user_in_db = await db_session.get(User, data["id"])
    assert user_in_db is not None
    yield user_in_db

    await db_session.delete(user_in_db)
    await db_session.commit()


@pytest_asyncio.fixture
async def authorize_second_user(async_client, db_session, second_user):
    login_data = {
        "username": second_user.username,
        "password": "hard_password"
    }

    login_resp = await async_client.post(
        "/auth/jwt/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert login_resp.status_code == 200

    access_token = login_resp.json()["access_token"]

    async_client.headers.update({
        "Authorization": f"Bearer {access_token}"
    })

    async_client.current_user = first_user

    return async_client


DEFAULT_CATEGORIES = {
    "Music",
    "Books",
    "Movies",
    "Sport",
    "Travel",
    "Economy"
}


@pytest_asyncio.fixture
async def seed_categories(db_session: AsyncSession):
    """
    Аналогично create_seed_categories в вашем коде.
    Создаём в тестовой БД все категории, если их ещё нет.
    """
    for cat_name in DEFAULT_CATEGORIES:
        result = await db_session.execute(select(Category).where(Category.name == cat_name))
        exists = result.scalars().first()
        if not exists:
            db_session.add(Category(name=cat_name))
    await db_session.commit()


@pytest_asyncio.fixture
async def first_post(async_client, db_session, first_user, seed_categories):
    payload = {
        "title": "Test post title",
        "content": "Test post description",
        "categories": ["Books"],
        "user_id": first_user.id,
    }
    response = await async_client.post("/posts/create/", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert "id" in data

    post_in_db = await db_session.get(Post, data["id"])
    assert post_in_db is not None
    yield post_in_db

    await db_session.delete(post_in_db)
    await db_session.commit()


@pytest_asyncio.fixture
async def second_post(async_client, db_session, first_user, seed_categories):
    payload = {
        "title": "Test second post title",
        "content": "Test second post description",
        "categories": ["Books"],
        "user_id": first_user.id,
    }
    response = await async_client.post("/posts/create/", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert "id" in data

    post_in_db = await db_session.get(Post, data["id"])
    assert post_in_db is not None
    yield post_in_db

    await db_session.delete(post_in_db)
    await db_session.commit()


@pytest_asyncio.fixture
async def authorized_client_with_post(async_client, db_session):
    user_data = {
        "email": "test_user1@mail.ru",
        "username": "test_user1",
        "password": "hard_password",
        "phone_number": "89298144304",
        "first_name": "John",
        "last_name": "Doe",
        "date_of_birth": "2000-01-01",
        "bio": "Bio"
    }

    reg_resp = await async_client.post("/auth/register", json=user_data)
    assert reg_resp.status_code in (201, 400)

    login_resp = await async_client.post(
        "/auth/jwt/login",
        data={"username": user_data["username"], "password": user_data["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    async_client.headers.update({
        "Authorization": f"Bearer {token}"
    })

    result = await db_session.execute(select(User).where(User.username == user_data["username"]))
    user = result.scalar_one()
    assert user is not None

    post = Post(
        title="Initial title",
        content="Initial content",
        user_id=user.id
    )
    db_session.add(post)
    await db_session.commit()
    await db_session.refresh(post)

    return async_client, post


@pytest_asyncio.fixture
async def authenticated_client(authorize_first_user):
    """
    Фикстура возвращает клиента, авторизованного с помощью authorize_first_user.
    """
    return authorize_first_user


@pytest_asyncio.fixture
async def first_comment(async_client, db_session, first_user, first_post):
    payload = {
        "text": "First test comment",
        "user_id": first_user.id,
        "post_id": first_post.id
    }

    response = await async_client.post("/comments/create/", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert 'id' in data

    comment_in_db = await db_session.get(Comment, data["id"])
    assert comment_in_db is not None

    yield comment_in_db

    await db_session.delete(comment_in_db)
    await db_session.commit()


@pytest_asyncio.fixture
async def second_comment(async_client, db_session, first_user, first_post):
    payload = {
        "text": "Second test comment",
        "user_id": first_user.id,
        "post_id": first_post.id
    }

    response = await async_client.post("/comments/create/", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert 'id' in data

    comment_in_db = await db_session.get(Comment, data["id"])
    assert comment_in_db is not None

    yield comment_in_db

    await db_session.delete(comment_in_db)
    await db_session.commit()


@pytest_asyncio.fixture
async def first_community(authenticated_client, db_session):
    payload = {
        "name": "Test first community",
        "description": "Test first community description"
    }

    response = await authenticated_client.post("/communities/create/", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert "community_id" in data

    community_in_db = await db_session.get(Community, data["community_id"])
    assert community_in_db is not None

    assert community_in_db.creator_id == authenticated_client.current_user.id

    yield community_in_db

    await db_session.delete(community_in_db)
    await db_session.commit()


@pytest_asyncio.fixture
async def second_community(authenticated_client, db_session):
    payload = {
        "name": "Test second community",
        "description": "Test second community description"
    }

    response = await authenticated_client.post("/communities/create/", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert "community_id" in data

    community_in_db = await db_session.get(Community, data["community_id"])
    assert community_in_db is not None

    assert community_in_db.creator_id == authenticated_client.current_user.id

    yield community_in_db

    await db_session.delete(community_in_db)
    await db_session.commit()
