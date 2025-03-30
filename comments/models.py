import datetime
from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, and_
from sqlalchemy.orm import relationship, foreign

from like_dislike.models import Like, Dislike
from settings import Base


class Comment(Base):
    __tablename__ = "comment"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    # Связи
    author = relationship("User", back_populates="comments")
    post_id = Column(Integer, ForeignKey("post.id"), nullable=False)
    post = relationship("Post", back_populates="comments")
    likes = relationship(
        "Like",
        primaryjoin=lambda: and_(
            foreign(Like.content_id) == Comment.id,
            Like.content_type == "comment"
        ),
        viewonly=True
    )
    dislikes = relationship(
        "Dislike",
        primaryjoin=lambda: and_(
            foreign(Dislike.content_id) == Comment.id,
            Dislike.content_type == "comment"
        ),
        viewonly=True
    )

    @property
    def likes_count(self):
        """Динамический подсчёт лайков комментария."""
        return len(self.likes) if self.likes else 0

    @property
    def dislikes_count(self):
        """Динамический подсчёт лайков комментария."""
        return len(self.dislikes) if self.dislikes else 0
