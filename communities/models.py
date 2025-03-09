from enum import Enum as PyEnum

from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship

from settings import Base


class CommunityRoleEnum(PyEnum):
    admin = "admin"
    moderator = "moderator"
    user = "user"


class CommunityMembership(Base):
    __tablename__ = "community_membership"

    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    community_id = Column(Integer, ForeignKey("community.id"), primary_key=True)
    role = Column(Enum(CommunityRoleEnum), nullable=False, default=CommunityRoleEnum.user)

    user = relationship("User", back_populates="community_memberships")
    community = relationship("Community", back_populates="community_memberships")


class Community(Base):
    __tablename__ = "community"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)

    creator_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    community_memberships = relationship(
        "CommunityMembership",
        back_populates="community",
        cascade="all, delete-orphan"
    )
    posts = relationship("Post", back_populates="communities")
    creator = relationship("User", back_populates="created_communities", foreign_keys=[creator_id])
