from pydantic import BaseModel


class CommentCreate(BaseModel):
    text: str
    user_id: int
    post_id: int


class CommentUpdate(BaseModel):
    text: str
