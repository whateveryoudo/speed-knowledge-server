"""知识库模型"""

from sqlalchemy import (
    Column,
    BigInteger,
    Boolean,
    Integer,
    String,
    DateTime,
    func,
    text,
)
from datetime import datetime
from app.db.base import Base

class Knowledge(Base):
    """知识库表

    Args:
        Base (_type_): 基类
    """

    __tablename__ = "knowledge_base"

    id = Column[int](BigInteger, primary_key=True, index=True, comment="主键")
    user_id = Column[str](String(255), index=True, nullable=False, comment="所属用户")
    name = Column[str](String(128), nullable=False, comment="知识库名称")
    slug = Column[str](String(64), nullable=True, comment="知识库短链")
    description = Column(String(512), nullable=True, comment="简介")
    cover_url = Column(String(255), nullable=True, comment="封面图")
    is_public = Column(
        Boolean, nullable=False, server_default=text("0"), comment="是否公开"
    )
    items_count = Column(
        Integer, nullable=False, server_default=text("0"), comment="文档数量"
    )
    content_updated_at = Column(DateTime, nullable=True, comment="内容最近更新时间")
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        comment="创建时间",
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),  # 或 mysql_on_update=func.current_timestamp()
        comment="更新时间",
    )
