import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import Field
from pydantic.v1 import BaseSettings
from pydantic_settings import SettingsConfigDict
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

class Settings(BaseSettings):
    db_host: str = Field(..., env="DB_HOST")
    db_port: str = Field(..., env="DB_PORT")
    db_name: str = Field(..., env="DB_NAME")
    db_user: str = Field(..., env="DB_USER")
    db_password: str = Field(..., env="DB_PASSWORD")

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    @property
    def database_url(self):
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
        )


@lru_cache()
def get_settings():
    return Settings()

engine = create_async_engine(get_settings().database_url, echo=True)
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_session():
    async with SessionLocal() as session:
        yield session


Base = declarative_base()

