import datetime
from sqlalchemy import MetaData, Column, Integer, String, DateTime, ForeignKey, func, Table, and_
from sqlalchemy.orm import relationship, foreign

from like_dislike.models import Like
from settings import Base

metadata = MetaData()

post_categories = Table(
    "post_categories",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("post.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("category.id"), primary_key=True)
)


class Post(Base):
    __tablename__ = "post"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    # Связи
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    categories = relationship("Category", secondary="post_categories", back_populates="posts")
    likes = relationship(
        "Like",
        primaryjoin=lambda: and_(
            foreign(Like.content_id) == Post.id,
            Like.content_type == "post"
        ),
        viewonly=True
    )

    @property
    def likes_count(self):
        return len(self.likes)
