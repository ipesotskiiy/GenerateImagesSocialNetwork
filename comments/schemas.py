from pydantic import BaseModel


class CommentCreate(BaseModel):
    text: str
    user_id: int
    post_id: int

    class Config:
        orm_mode = True


class CommentRead(BaseModel):
    id: int
    text: str
    user_id: int
    post_id: int
    likes_count: int
    dislikes_count: int

    class Config:
        orm_mode = True


class CommentUpdate(BaseModel):
    text: str

    class Config:
        orm_mode = True


class CommentDelete(BaseModel):
    status: str
    id: int
