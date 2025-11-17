"""附件相关"""

from fastapi import APIRouter, status, Depends, UploadFile, File
from sqlalchemy.orm.session import Session
from app.services.attachment_service import AttachmentService
from app.models.user import User
from app.core.security import get_current_user
from app.schemas.attachment import AttachmentResponse, AttachmentCreate

router = APIRouter()


@router.post(
    "/upload/single",
    response_model=AttachmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_attachment(
    file: UploadFile = File(...), current_user: User = Depends(get_current_user)
):
    """上传附件"""
    metadata = AttachmentCreate(
        file_name=file.filename,
        file_type=file.content_type,
        object_key=file.filename,
    )
    attachment = AttachmentService.create(metadata, file, current_user)
    return attachment


@router.get("/{attachment_id}")
async def get_attachment(attachment_id: str):
    """获取附件"""
    attachment = AttachmentService.get(attachment_id)
    return attachment
