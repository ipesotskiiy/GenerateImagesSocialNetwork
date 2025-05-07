from functools import lru_cache
from pathlib import Path
from typing import AsyncGenerator

import redis
from pydantic import Field
from pydantic.v1 import BaseSettings
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from fastapi_users.authentication import BearerTransport


class Settings(BaseSettings):
    DB_HOST: str = Field(..., env="DB_HOST")
    DB_PORT: str = Field(..., env="DB_PORT")
    DB_NAME: str = Field(..., env="DB_NAME")
    DB_USER: str = Field(..., env="DB_USER")
    DB_PASSWORD: str = Field(..., env="DB_PASSWORD")

    REDIS_URL: str = Field(..., env="REDIS_URL")
    SECRET: str = Field(..., env="SECRET")

    @property
    def db_async_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def db_sync_url(self) -> str:
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    base_dir: Path = Path(__file__).resolve().parent
    media_dir: Path = base_dir / "media"

    media_avatar_dir: Path = media_dir / "avatar"
    media_temp_avatar_dir: Path = media_dir / "avatars_tmp"

    media_user_photos_dir: Path = media_dir / "user_photo"
    media_temp_user_photos_dir: Path = media_dir / "user_photos_tmp"

    media_comment_images_dir: Path = media_dir / "comment_images"
    media_temp_comment_images_dir: Path = media_dir / "comment_images_tmp"

    media_post_images_dir: Path = media_dir / "post_images"
    media_temp_post_images_dir: Path = media_dir / "post_images_tmp"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache  # каждый воркер Uvicorn получит ровно один объект Settings
def get_settings() -> Settings:
    return Settings()

settings = get_settings()

Base = declarative_base()

sync_engine = create_engine(settings.db_sync_url)
sync_session = sessionmaker(bind=sync_engine)

async_engine = create_async_engine(settings.db_async_url, echo=False)
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)

redis_database = redis.from_url(settings.REDIS_URL, decode_responses=True)
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
#
# load_dotenv()
#
# # Database settings
# DB_HOST = os.environ.get("DB_HOST")
# DB_PORT = os.environ.get("DB_PORT")
# DB_NAME = os.environ.get("DB_NAME")
# DB_USER = os.environ.get("DB_USER")
# DB_PASSWORD = os.environ.get("DB_PASSWORD")
# DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# DATABASE_SYNC_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# Base = declarative_base()
#
# sync_engine = create_engine(DATABASE_SYNC_URL)
# sync_session = sessionmaker(bind=sync_engine)
#
# engine = create_async_engine(DATABASE_URL)
# async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
#
# redis_database = redis.Redis(host="localhost", port=6379, db=1)
# redis_url = os.environ.get("REDIS_URL")
#
# BASE_DIR = Path(__file__).resolve().parent
# MEDIA_URL = os.path.join(BASE_DIR, "media")
# MEDIA_AVATAR_URL = os.path.join(MEDIA_URL, "avatar")
# MEDIA_TEMP_AVATAR_URL = os.path.join(MEDIA_URL, "avatars_tmp")
# MEDIA_USER_PHOTOS_URL = os.path.join(MEDIA_URL, "user_photo")
# MEDIA_TEMP_USER_PHOTOS_URL = os.path.join(MEDIA_URL, "user_photos_tmp")
# MEDIA_COMMENT_IMAGES_URL = os.path.join(MEDIA_URL, "comment_images")
# MEDIA_TEMP_COMMENT_IMAGES_URL = os.path.join(MEDIA_URL, "comment_images_tmp")
# MEDIA_POST_IMAGES_URL = os.path.join(MEDIA_URL, "post_images")
# MEDIA_TEMP_POST_IMAGES_URL = os.path.join(MEDIA_URL, "post_images_tmp")
#
#
# SECRET = "SECRET"
# bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
#
#
# async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
#     async with async_session_maker() as session:
#         yield session

