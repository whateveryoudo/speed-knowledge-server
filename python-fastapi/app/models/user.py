"""用户模型"""

from sqlalchemy import Column, Integer, String, DateTime, func
from app.db.base import Base
from sqlalchemy.orm import relationship
from app.core.mixins import SoftDeleteMixin

class User(Base, SoftDeleteMixin):
    """用户表

    Args:
        Base (_type_): 基类
    """

    __tablename__ = "user"

    id = Column[int](Integer, primary_key=True, index=True)
    email = Column[str](String(255), unique=True, index=True, nullable=False)
    username = Column[str](String(255), unique=True, index=True, nullable=False)
    password = Column[str](String(255), nullable=False)
    nickname = Column[str](String(255), nullable=True)  # 昵称，可选，不唯一
    created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False)

    documents = relationship("Document", back_populates="user", cascade="all, delete")
    collects = relationship("Collect", back_populates="user", cascade="all, delete")
    knowledge_collaborators = relationship("KnowledgeCollaborator", back_populates="user")
    space_members = relationship("SpaceMember", back_populates="user")
    team_members = relationship("TeamMember", back_populates="user")