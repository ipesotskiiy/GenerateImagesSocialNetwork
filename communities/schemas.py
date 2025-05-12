from typing import Optional
from pydantic import BaseModel


class BaseCommunity(BaseModel):
    name: str
    description: Optional[str] = None


class CreateCommunity(BaseCommunity):
    pass

class ReadCommunity(BaseCommunity):
    id: int
    creator_id: int

    class Config:
        orm_mode = True


class UpdateCommunity(BaseCommunity):
    class Config:
        orm_mode = True

class CommunityDelete(BaseModel):
    status: str
    id: int

class AssignModerator(BaseModel):
    status: str
    user_id: int
    role: str

class RemoveUser(BaseModel):
    status: str
    user_id: int

class ToggleSubscription(BaseModel):
    status: str
    community_id: int
