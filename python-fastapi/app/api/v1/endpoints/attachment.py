"""附件相关"""

from fastapi import APIRouter, status, Depends, UploadFile, File, HTTPException, Request
from sqlalchemy.orm.session import Session
from fastapi.responses import StreamingResponse
from app.services.attachment_service import AttachmentService
from app.models.user import User
from app.core.deps import get_current_user, get_db, get_current_user_from_query
from app.schemas.attachment import AttachmentResponse, AttachmentCreate
from app.services.onlyoffice_service import OnlyofficeService
from app.core.template import template
from app.core.config import settings
import urllib.parse

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
    print(f"fileContentLength: {len(file.content_type)}")
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
    file_info = AttachmentService(db).getStream(attachment_id)
    if not file_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="附件不存在")
    fallback = urllib.parse.quote(file_info["file_name"].encode('utf-8'))
    return StreamingResponse(
        file_info["data_stream"],
        media_type=file_info["file_type"],
        headers={
            "Content-Disposition": f"inline;filename*=UTF-8''{fallback}",
        },
    )


@router.get("/download/{attachment_id}")
async def download_attachment(
    attachment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """下载附件"""
    file_info = AttachmentService(db).getStream(attachment_id)
    if not file_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="附件不存在")
    
    fallback = urllib.parse.quote(file_info["file_name"].encode('utf-8'))
    return StreamingResponse(
        file_info["data_stream"],
        media_type=file_info["file_type"],
        headers={
            "Content-Disposition": f"attachment;filename*=UTF-8\'\'{fallback}",
        },
    )


@router.get("/onlyoffice/file-preview/{attachment_id}")
async def get_onlyoffice_file_preview(
    request: Request,
    attachment_id: str,
    current_user: User = Depends(get_current_user_from_query),
    db: Session = Depends(get_db),
):
    """获取文件预览(onlyoffice版本)"""
    file_info = AttachmentService(db).get(attachment_id)
    onlyoffice_service = OnlyofficeService(db)
    config = onlyoffice_service.generate_config(
        file_info, "view", request.query_params.get("access_token")
    )

    return template.TemplateResponse(
        "onlyoffice_preview.html",
        {
            "request": request,
            "onlyofficeServerUrl": settings.ONLYOFFICE_SERVER_URL,
            "config": config,
            "fileName": file_info.file_name,
            "fileSizeMB": file_info.file_size / 1024 / 1024,
            "fileType": file_info.file_type,
        },
    )
