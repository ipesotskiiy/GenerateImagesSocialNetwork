import datetime

from sqlalchemy import MetaData, Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from settings import Base

metadata = MetaData()


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
