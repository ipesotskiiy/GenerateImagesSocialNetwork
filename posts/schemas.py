import datetime
from typing import Optional

from pydantic import BaseModel


class PostCreate(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime.datetime


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
