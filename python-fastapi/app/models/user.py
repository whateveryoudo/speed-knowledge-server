"""用户模型"""

from sqlalchemy import Column, Integer, String, DateTime, func
from datetime import datetime
from app.db.base import Base
from zoneinfo import ZoneInfo


class User(Base):
    """用户表

    Args:
        Base (_type_): 基类
    """

    __tablename__ = "users"

    id = Column[int](Integer, primary_key=True, index=True)
    email = Column[str](String(255), unique=True, index=True, nullable=False)
    password = Column[str](String(255), unique=True, index=True, nullable=False)
    name = Column[str](String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False)
