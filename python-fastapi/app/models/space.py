from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime, Enum, JSON, func, ForeignKey, Integer
from app.db.base import Base
from app.core.mixins import SoftDeleteMixin
from app.common.enums import SpaceType
from app.schemas.attachment import default_attachment_item
from sqlalchemy.orm import relationship


class Space(SoftDeleteMixin, Base):
    __tablename__ = "space"
    id = Column(String(36), default=lambda: str(uuid.uuid4()), primary_key=True)
    type = Column(
        Enum(SpaceType), default=SpaceType.PERSONAL, nullable=False, comment="空间类型"
    )
    domain = Column(
        String(64), nullable=True, unique=True, comment="空间域名,也用于标识访问(可选,个人类型可不传入domin)"
    )
    name = Column(String(64), nullable=False, comment="空间名称")
    owner_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, comment="空间所有者ID")
    contact_email = Column(String(255), nullable=False, comment="联系邮箱,用于接收通知")
    icon = Column(
        JSON,
        default=default_attachment_item.model_dump(),
        nullable=True,
        comment="封面图信息",
    )
    description = Column(String(512), nullable=False, comment="空间描述")
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
        comment="更新时间",
    )

    space_members = relationship("SpaceMember", back_populates="space", cascade="all, delete")