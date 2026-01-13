"""附件模型"""

from sqlalchemy import (Column,
    BigInteger,
    Boolean,
    Integer,
    String,
    DateTime,
    func,
    text)
from app.db.base import Base    
from datetime import datetime
import uuid

class Attachment(Base):
    """附件表

    Args:
        Base (_type_): _description_
    """
    __tablename__ = "attachment"

    id = Column[str](String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True, comment="主键")
    file_name = Column[str](String(255), index=True, comment="附件名称")
    file_type = Column[str](String(255), comment="附件类型")
    object_name= Column[str](String(255), nullable = False, comment="文件的唯一标识路径")
    file_size = Column[int](BigInteger, comment="附件大小")
    bucket_name = Column[str](String(255), nullable = False, comment = 'bucket名')
    user_id = Column[int](Integer, index=True, nullable=False, comment="上传者")
    created_at = Column[datetime](
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        comment="创建时间",
    ) 
    updated_at = Column[datetime](
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),  # 或 mysql_on_update=func.current_timestamp()
        comment="更新时间",
    )