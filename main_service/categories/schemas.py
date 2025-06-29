from typing import Optional

from pydantic import BaseModel


class CategoryBase(BaseModel):
    id: int
    name: Optional[str]

    class Config:
        orm_mode = True


class CategoryRead(BaseModel):
    name: Optional[str]

    class Config:
        orm_mode = True
