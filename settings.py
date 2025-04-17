import os
import logging
from pathlib import Path
from typing import AsyncGenerator

import redis
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Database settings
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
DATABASE_SYNC_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
Base = declarative_base()

sync_engine = create_engine(DATABASE_SYNC_URL)
sync_session = sessionmaker(bind=sync_engine)

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

redis_database = redis.Redis(host="localhost", port=6379, db=1)
redis_url = os.environ.get("REDIS_URL")

BASE_DIR = Path(__file__).resolve().parent
MEDIA_URL = os.path.join(BASE_DIR, "media")
MEDIA_AVATAR_URL = os.path.join(MEDIA_URL, "avatar")
MEDIA_TEMP_AVATAR_URL = os.path.join(MEDIA_URL, "avatars_tmp")


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

