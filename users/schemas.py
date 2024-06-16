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
    password: str
    registered_at: str
