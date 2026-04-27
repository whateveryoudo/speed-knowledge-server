from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm.session import Session
from app.core.deps import get_db, get_current_user, vertify_document_permission
from app.schemas.internal import InternalQueryInDocumentValid
from app.common.enums import DocumentAbility
from app.models.user import User

router = APIRouter()


@router.get(
    "/document/{document_id}/valid",
    response_model=bool,
    status_code=status.HTTP_200_OK,
)
def validate_document_edit_permission(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> bool:
    """获取权限(这里是提供给nodejs服务的，用于验证文档编辑权限，协同使用)"""

    return vertify_document_permission(
        DocumentAbility.DOC_EDIT, document_id, current_user, db
    )
