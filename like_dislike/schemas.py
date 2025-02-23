from typing import Literal

from pydantic import BaseModel


class LikeBase(BaseModel):
    user_id: int
    content_id: int
    content_type: Literal["post", "comment"]


class LikeCreate(LikeBase):
    pass


class LikeResponse(LikeBase):
    id: int

    class Config:
        orm_mode = True
