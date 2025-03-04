from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship

from settings import Base

user_community = Table(
    'user_community', Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id'), primary_key=True),
    Column('community_id', Integer, ForeignKey('community.id'), primary_key=True)
)


class Community(Base):
    __tablename__ = "community"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)

    users = relationship("User", secondary=user_community, back_populates="communities")
    posts = relationship("Post", back_populates="communities")
