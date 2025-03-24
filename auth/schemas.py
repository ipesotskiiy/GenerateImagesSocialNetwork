from datetime import date
from typing import Optional

from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    id: int
    email: str
    username: str
    date_of_birth: Optional[date]
    age: Optional[int]
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
    date_of_birth: Optional[date]
    bio: Optional[str]
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False