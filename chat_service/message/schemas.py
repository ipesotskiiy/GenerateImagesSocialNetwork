from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class MessageBase(BaseModel):
    recipient_id: int = Field(..., ge=1)
    content: str = Field(..., min_length=1, max_length=4000)


class MessageCreate(MessageBase):
    """Тело запроса на создание сообщения."""
    sender_id: int


class MessageUpdate(BaseModel):
    """Тело запроса на частичное обновление сообщения."""
    content: Optional[str] = Field(None, min_length=1, max_length=4000)

    model_config = ConfigDict(extra="forbid")


class MessageRead(MessageBase):
    """Ответ со стороны API/БД."""
    id: int
    sender_id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)