from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy import Null
from sqlalchemy.orm.session import Session

from app.core.deps import get_db, get_current_user, VertifyDocumentPermission
from app.schemas.internal import InternalQueryInDocumentValid
from app.common.enums import DocumentAbility
from app.models.user import User
from app.core.deps import verify_internal_token, idempency_interceptor_key
from app.models.document import Document

router = APIRouter()


@router.get(
    "/document/{identifier}/valid",
    response_model=bool,
    status_code=status.HTTP_200_OK,
)
def validate_document_edit_permission(
    current_user: User = Depends(get_current_user),
    internal_token: bool = Depends(verify_internal_token),
    document: Document = Depends(VertifyDocumentPermission(DocumentAbility.DOC_EDIT)),
    db: Session = Depends(get_db),
) -> bool:
    """获取权限(这里是提供给nodejs服务的，用于验证文档编辑权限，协同使用)"""
    return document is not Null
