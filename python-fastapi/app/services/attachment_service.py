"""附件服务"""

import email
from fastapi import UploadFile, HTTPException
from typing import Optional, Dict, Any
from sqlalchemy.orm.session import Session
from app.models.attachment import Attachment
from app.schemas.attachment import AttachmentCreate, AttachmentStream
from app.core.minio_client import get_minio
from app.models.user import User
from datetime import datetime, timedelta
import uuid


class AttachmentService:
    """附件服务类"""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.minio = get_minio()

    def create(
        self, attachment_in: AttachmentCreate, file: UploadFile, current_user: User
    ) -> Attachment:
        """上传附件

        Args:
            attachment_in (AttachmentCreate): 入参
            user (User): 用户
        Returns:
            Attachment: 附件
        """
        object_name = f"{current_user.id}/{str(uuid.uuid4())}_{attachment_in.file_name}"
        # file: UploadFile
        file_obj = file.file  # 这是一个类文件对象 (SpooledTemporaryFile)
        file_obj.seek(0, 2)  # 移到末尾
        size = file_obj.tell()
        file_obj.seek(0)  # 回到开头，准备读
        self.minio.put_object(
            bucket_name=attachment_in.bucket_name,
            data=file_obj,
            length=size,
            content_type=attachment_in.file_type,
            object_name=object_name,
        )

        attachment = Attachment(
            file_name=attachment_in.file_name,
            file_type=attachment_in.file_type,
            file_size=size,
            bucket_name=attachment_in.bucket_name,
            object_name=object_name,
            user_id=current_user.id,
        )

        self.db.add(attachment)
        self.db.commit()
        self.db.refresh(attachment)
        return attachment

    def getStream(self, attachment_id: str) -> AttachmentStream:
        """获取附件流"""
        attachment = (
            self.db.query(Attachment).filter(Attachment.id == attachment_id).first()
        )
        if not attachment:
            raise HTTPException(status_code=404, detail="未找到附件")

        return {
            "data_stream": self.minio.get_object(attachment.bucket_name, attachment.object_name),
            "file_type": attachment.file_type,
            "file_name": attachment.file_name,
        }

    def get(self, attachment_id: str) -> Attachment:
        """获取附件记录"""
        attachment = (
            self.db.query(Attachment).filter(Attachment.id == attachment_id).first()
        )
        if not attachment:
            raise HTTPException(status_code=404, detail="未找到附件")
        return attachment
