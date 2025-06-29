from functools import lru_cache

from pydantic import Field
from pydantic.v1 import BaseSettings
from pydantic_settings import SettingsConfigDict


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
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


@lru_cache()
def get_settings():
    return Settings()

