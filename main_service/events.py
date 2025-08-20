from datetime import datetime
from typing import Literal, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict

class ChatEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    v: int = 1
    type: Literal["new", "edit", "delete"]
    id: int
    sender_id: int
    recipient_id: int
    content: Optional[str] = None
    timestamp: datetime
    event_id: UUID = Field(default_factory=uuid4)
