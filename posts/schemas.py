from typing import List, Optional
import datetime

from pydantic import BaseModel


class PostCreate(BaseModel):
    title: str
    content: str
    categories: List[str]
    user_id: int

    class Config:
        orm_mode = True


class PostRead(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    categories: List[str] = None
    user_id: int
    likes_count: int

    class Config:
        orm_mode = True


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    categories: List[str] = None

    class Config:
        orm_mode = True
