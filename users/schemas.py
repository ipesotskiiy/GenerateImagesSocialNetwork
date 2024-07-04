from fastapi_users import schemas
from pydantic import (
    BaseModel,
    EmailStr,
)


class UserSchema(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    username: str
    phone_number: str
    hashed_password: str
    registered_at: str


class UserRead(schemas.BaseUser[int]):
    username: str
    registered_at: str



class UserCreate(schemas.BaseUserCreate):
    username: str
    phone_number: str

