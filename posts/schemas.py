from typing import Optional

from pydantic import BaseModel


class PostCreate(BaseModel):
    title: str
    content: str
    user_id: int


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
