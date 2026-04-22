from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Index, JSON, Integer, UniqueConstraint
from app.db.base import Base
import uuid
from datetime import datetime
from app.common.enums import NotificationBizType, NotificationListType
from app.db.base import Base
from sqlalchemy.orm import relationship
class Notification(Base):
    """通知模型(用于记录用户收到的通知，用于后续的通知管理、通知发送、通知阅读等操作)
    """
    __tablename__ = "notification"

    __table_args__ = (
        UniqueConstraint("mentioned_user_id", "biz_type", "biz_id", name="uix_mentioned_user_id_biz_type_biz_id"),
        Index("idx_mentioned_user_id_created_at", "mentioned_user_id", "created_at"),
        Index("idx_mentioned_user_id_read_at", "mentioned_user_id", "read_at"),
    )

    id: Column[String(36)] = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid7()), comment="通知id")
    actor_user_id: Column[int] = Column(Integer, ForeignKey("user.id"), index=True, comment="发起者用户id")
    mentioned_user_id: Column[int] = Column(Integer, ForeignKey("user.id"), index=True, comment="被提及用户id")
    biz_type: Column[NotificationBizType] = Column(String(20), nullable=False, comment="业务类型")
    list_type: Column[NotificationListType] = Column(String(20), nullable=False, comment="列表类型(用于分组展示)")
    biz_id: Column[String(36)] = Column(String(128), index=True, comment="业务id(用于幂等性)")
    read_at: Column[DateTime] = Column(DateTime, nullable=True, comment="已读时间")
    payload: Column[JSON] = Column(JSON, nullable=True, comment="负载(扩展数据，携带到跳转链接的参数)")
    created_at: Column[DateTime] = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at: Column[DateTime] = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


    actor_user = relationship("User", foreign_keys=[actor_user_id])
    mentioned_user = relationship("User", foreign_keys=[mentioned_user_id])