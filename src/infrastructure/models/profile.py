from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from datetime import datetime, UTC
from uuid import uuid4

from src.infrastructure.context.sql_db.psql_dbcontext import Base


class Profile(Base):
    __tablename__ = "profile"

    id = Column(
        String(36), primary_key=True, index=True, default=lambda: str(uuid4())
    )
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)

    creation_datetime = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        default=datetime.now(UTC),
    )
    modification_datetime = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=True,
        onupdate=datetime.now(UTC),
    )
