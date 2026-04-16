from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Index, JSON, Integer, UniqueConstraint
from app.db.base import Base
import uuid
from datetime import datetime
from app.common.enums import NotificationBizType
from app.db.base import Base

class Notification(Base):
    """通知模型(用于记录用户收到的通知，用于后续的通知管理、通知发送、通知阅读等操作)
    """
    __tablename__ = "notification"

    __table_args__ = (
        UniqueConstraint("user_id", "biz_type", "biz_id", name="uix_user_id_biz_type_biz_id"),
        Index("idx_user_id_created_at", "user_id", "created_at"),
        Index("idx_user_id_read_at", "user_id", "read_at"),
    )

    id: Column[String(36)] = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid7()), comment="通知id")
    mentioned_user_id: Column[int] = Column(Integer, ForeignKey("user.id"), index=True, comment="被提及用户id")
    biz_type: Column[NotificationBizType] = Column(String(20), nullable=False, comment="业务类型")
    biz_id: Column[String(36)] = Column(String(36), index=True, comment="业务id(用于幂等性)")
    title: Column[String(255)] = Column(String(255), nullable=False, comment="标题")
    content: Column[Text] = Column(Text, nullable=True, comment="内容")
    read_at: Column[DateTime] = Column(DateTime, nullable=True, comment="已读时间")
    payload: Column[JSON] = Column(JSON, nullable=True, comment="负载(扩展数据，携带到跳转链接的参数)")
    created_at: Column[DateTime] = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at: Column[DateTime] = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
