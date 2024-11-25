import datetime

from sqlalchemy import MetaData, Column, Integer, String, LargeBinary, DateTime, ForeignKey, Table

from auth.models import User

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

post = Table(
    "post",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String),
    Column("content", String),
    Column("created_at", DateTime(timezone=True), default=datetime.datetime.now()),
    Column("updated_at", DateTime(timezone=True), nullable=True),
    Column("user_id", Integer, ForeignKey(User.id), nullable=True),
    Column("attachment", LargeBinary, nullable=True)
)