"""附件模型"""

from typing import Optional
from sqlalchemy import (
    BigInteger,
    Integer,
    String,
    DateTime,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from datetime import datetime
import uuid


class Attachment(Base):
    """附件表

    Args:
        Base (_type_): _description_
    """

    __tablename__ = "attachment"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
        comment="主键",
    )
    file_name: Mapped[Optional[str]] = mapped_column(
        String(255), index=True, comment="附件名称"
    )
    file_type: Mapped[Optional[str]] = mapped_column(
        String(255), comment="附件类型"
    )
    object_name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="文件的唯一标识路径"
    )
    file_size: Mapped[Optional[int]] = mapped_column(
        BigInteger, comment="附件大小"
    )
    bucket_name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="bucket名"
    )
    user_id: Mapped[int] = mapped_column(
        Integer, index=True, nullable=False, comment="上传者"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        comment="创建时间",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),
        comment="更新时间",
    )