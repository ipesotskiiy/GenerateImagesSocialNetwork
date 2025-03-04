from typing import Optional

from pydantic import BaseModel


class BaseCommunity(BaseModel):
    name: str
    description: Optional[str]


class CreateCommunity(BaseCommunity):
    pass


class ReadCommunity(BaseCommunity):
    id: int

    class Config:
        orm_mode = True


class UpdateCommunity(BaseCommunity):

    class Config:
        orm_mode = True

