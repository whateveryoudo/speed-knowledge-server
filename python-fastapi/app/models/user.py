"""用户模型"""
from datetime import datetime
from app.db.base import Base
from sqlalchemy import Column,Integer,String, DateTime

class User(Base):
    """用户表"""
    
    ___tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True,index=True, nullable=False)
    password = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    create_at = Column(DateTime, default=datetime.utcnow,nullable=False)
    update_at = Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow, nullable=False)