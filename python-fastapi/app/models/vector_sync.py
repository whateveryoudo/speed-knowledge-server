from sqlalchemy import Column, String, func, text
from sqlalchemy.dialects.mysql import DATETIME
from app.db.base import Base
from datetime import datetime


class VectorSync(Base):
    """向量同步模型(用于mq推送)"""

    __tablename__ = "vector_sync"

    document_id = Column[str](
        String(36), primary_key=True, index=True, comment="文档ID(这里用于主键)"
    )


    knowledge_id = Column[str](
        String(36), index=True, comment="所属知识库ID"
    )
    last_content_updated_at = Column[datetime](
        DATETIME(fsp=3), nullable=False, comment="最后一次内容更新时间"
    )
    next_run_at = Column[datetime](
        DATETIME(fsp=3),
        nullable=False,
        index=True,
        comment="下次运行时间(定时任务调度)",
    )
    locked_at = Column[datetime](
        DATETIME(fsp=3), nullable=True, default=None, comment="锁定时间"
    )
    lock_token = Column[str](
        String(36), nullable=True, default=None, comment="锁定令牌"
    )
    updated_at = Column[datetime](
        DATETIME(fsp=3),
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP(3)'),
        onupdate=datetime.utcnow,
        comment="更新时间",
    )
