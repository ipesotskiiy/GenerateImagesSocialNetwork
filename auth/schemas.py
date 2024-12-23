from typing import Optional

from fastapi_users import schemas
from pydantic import conint, Field


class UserRead(schemas.BaseUser[int]):
    id: int
    email: str
    username: str
    bio: Optional[str]
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False


class UserCreate(schemas.BaseUserCreate):
    email: str
    username: str
    phone_number: str
    password: str
    first_name: str
    last_name: str
    age: Optional[conint(ge=1, le=120)] = Field(..., description="Возраст должен быть в диапазоне от 1 до 120 лет")
    bio: Optional[str]
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False