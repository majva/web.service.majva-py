from sqlalchemy import Column, Integer, String, DateTime, Boolean
from src.infrastructure.context.dbcontext import Base
from sqlalchemy.sql import func
from datetime import datetime, UTC
from uuid import uuid4

class Account(Base):
    __tablename__ = "account"

    id = Column(
        String(36), primary_key=True, index=True, default=lambda: str(uuid4())
    )
    user_id = Column(String, unique=True, nullable=False, index=True)
    user_name = Column(String, unique=True, nullable=False, index=True)

    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    photo_url = Column(String(300), nullable=True)

    team_name = Column(String(80), nullable=True)
    department_name = Column(String(80), nullable=True)
    active = Column(Boolean, default=False)

    creation_datetime = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, default=datetime.now(UTC))
    modification_datetime = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)