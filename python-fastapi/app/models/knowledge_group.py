"""知识库分组模型"""

from sqlalchemy import Column, Integer, String, JSON, text, Boolean, func, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.schemas.knowledge_group import DEFAULT_DISPLAY_CONFIG

class KnowledgeGroup(Base):
    """知识库分组模型"""

    __tablename__ = "knowledge_groups"
    id = Column(Integer, primary_key=True, index=True, comment="分组ID")
    user_id = Column(String(255), index=True, comment="用户ID")
    group_name = Column(String(255), default="新建分组", index=True, comment="分组名称")
    order_index = Column(Integer, default=0, server_default=text('0'), comment="排序索引")
    is_default = Column(Boolean, default=False, comment="是否默认分组")
    created_at = Column(DateTime, server_default=func.current_timestamp(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), comment="更新时间")

    display_config = Column(JSON, default=DEFAULT_DISPLAY_CONFIG, nullable=True, comment="显示配置")
    knowledge_items = relationship("Knowledge", back_populates="group", cascade="all, delete")
    