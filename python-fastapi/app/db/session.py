"""数据库会话"""

from sqlalchemy import create_engine
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(url=settings.DATABASE_URL,  pool_pre_ping=True)
SessionLocal = sessionmaker[Session](autocommit=False, autoflush=False, bind=engine)
