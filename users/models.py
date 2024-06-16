from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    TIMESTAMP
)

from settings import Base


class User(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    first_name = Column(String(25))
    last_name = Column(String(25))
    email = Column(String(40), index=True, unique=True, nullable=False)
    username = Column(String(40), index=True, unique=True, nullable=False)
    phone_number = Column(String(10))
    password = Column(String(250), nullable=False)
    registered_at = Column(TIMESTAMP, default=datetime.utcnow)
