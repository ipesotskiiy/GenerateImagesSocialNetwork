import datetime

from sqlalchemy import MetaData, Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from settings import Base

metadata = MetaData()


# class Post(Base):
#     __tablename__ = 'posts'
#
#     id = Column(Integer, primary_key=True)
#     title = Column(String)
#     content = Column(String)
#     created_at = Column(DateTime, default=datetime.datetime.now())
#     updated_at = Column(DateTime, nullable=True)
#     user_id = Column(Integer, ForeignKey(User.id))
#     attachment = Column(LargeBinary, nullable=True)

# post = Table(
#     "post",
#     metadata,
#     Column("id", Integer, primary_key=True),
#     Column("title", String),
#     Column("content", String),
#     Column("created_at", DateTime(timezone=True), default=datetime.datetime.now()),
#     Column("updated_at", DateTime(timezone=True), nullable=True),
#     Column("user_id", Integer, ForeignKey(User.id), nullable=True),
#     Column("attachment", LargeBinary, nullable=True)
# )

class Post(Base):
    __tablename__ = "post"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=True)

    # Внешний ключ для связи с User
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    # Отношение к User
    author = relationship("User", back_populates="posts")