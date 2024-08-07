from datetime import datetime

from sqlalchemy import MetaData, Integer, String, TIMESTAMP, Boolean
from sqlalchemy.testing.schema import Table, Column

metadata = MetaData()

user = Table(
    'user',
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, nullable=False),
    Column("username", String, nullable=False),
    Column("first_name", String(20)),
    Column("last_name", String(30)),
    Column("phone_number", String(12), nullable=False),
    Column("registered_at", TIMESTAMP, default=datetime.utcnow),
    Column("hashed_password", String(length=1024), nullable=False),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("is_superuser", Boolean, default=False, nullable=False),
    Column("is_verified", Boolean, default=False, nullable=False)
)