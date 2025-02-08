from tokenize import String

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from settings import Base


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    posts = relationship("Post", secondary="post_categories", back_populates="categories")
