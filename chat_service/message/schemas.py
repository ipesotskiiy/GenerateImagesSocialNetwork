from datetime import datetime

from pydantic import BaseModel


class MessageBase(BaseModel):
    content: str
    recipient_id: int


class MessageCreate(MessageBase):
    pass


class MessageRead(MessageBase):
    id: int
    sender_id: int
    timestamp: datetime

    class Config:
        orm_mode = True