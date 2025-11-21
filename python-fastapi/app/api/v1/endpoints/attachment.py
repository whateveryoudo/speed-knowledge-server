"""附件相关"""

from fastapi import APIRouter, status, Depends, UploadFile, File
from sqlalchemy.orm.session import Session
from fastapi.responses import StreamingResponse
from app.services.attachment_service import AttachmentService
from app.models.user import User
from app.core.deps import get_current_user, get_db, get_current_user_from_query
from app.schemas.attachment import AttachmentResponse, AttachmentCreate
import io

router = APIRouter()


@router.post(
    "/upload/single",
    response_model=AttachmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_attachment(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """上传附件"""
    metadata = AttachmentCreate(
        file_name=file.filename,
        file_type=file.content_type,
        object_name=file.filename,
    )
    attachment_service = AttachmentService(db)
    attachment = attachment_service.create(metadata, file, current_user)
    return attachment


@router.get("/preview/{attachment_id}")
async def get_attachment(
    attachment_id: str,
    current_user: User = Depends(get_current_user_from_query),
    db: Session = Depends(get_db),
):
    """获取附件"""
    file_info = AttachmentService(db).get(attachment_id)
    return StreamingResponse(
        file_info["data_stream"],
        media_type=file_info["content_type"],
        headers={
            "Content-Disposition": f"attachment; filename={file_info['filename']}",
        },
    )
