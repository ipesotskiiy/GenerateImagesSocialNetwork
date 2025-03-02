from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from settings import Base


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    content_id = Column(Integer, nullable=False)  # ID поста или комментария
    content_type = Column(String, nullable=False)  # "post" или "comment"

    user = relationship("User", back_populates="likes")


class Dislike(Base):
    __tablename__ = "dislike"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    content_id = Column(Integer, nullable=False)
    content_type = Column(String, nullable=False)

    user = relationship("User", back_populates='dislikes')
