from datetime import datetime, date
from typing import Optional

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, Date
from sqlalchemy.orm import relationship

from settings import Base


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, unique=True, index=True)
    username = Column(String, nullable=False, unique=True)
    first_name = Column(String(20))
    last_name = Column(String(30))
    phone_number = Column(String(12), nullable=False, unique=True, index=True)
    bio = Column(String(2000))
    date_of_birth = Column(Date, nullable=True)
    registered_at = Column(TIMESTAMP, default=datetime.utcnow)
    hashed_password = Column(String(length=1024), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="user")

    @property
    def age(self) -> Optional[int]:
        """Вычисляет возраст на основе даты рождения."""
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
