import os
import logging
from typing import AsyncGenerator

import redis
from celery import Celery
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Database settings
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
Base = declarative_base()

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

redis_database = redis.Redis(host="localhost", port=6379, db=1)
redis_url = os.environ.get("REDIS_URL")

celery_app = Celery(
    'celery_worker',
    broker=redis_url,
    backend=redis_url
)

# celery_app.autodiscover_tasks(["/tasks.tasks.py"])
celery_app.conf.update(result_expires=10000)



async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

