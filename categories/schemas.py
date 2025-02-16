from typing import Optional

from pydantic import BaseModel


class GenreBase(BaseModel):
    id: int
    name: Optional[str]

    class Config:
        orm_mode = True