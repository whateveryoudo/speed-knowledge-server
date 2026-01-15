"""首页接口"""

from fastapi import APIRouter, Depends
from app.models.user import User
from sqlalchemy.orm.session import Session
from app.core.deps import get_current_user, get_db
from app.services.document_history import DocumentHistoryService
from app.schemas.document_history import DocumentHistoryQuery
from app.schemas.response import PaginationResponse
from app.schemas.document_history import DocumentHistoryResponse

router = APIRouter()

@router.post("/document-history-list", response_model=PaginationResponse)
async def get_document_history_list(
    query_in: DocumentHistoryQuery,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PaginationResponse[DocumentHistoryResponse]:
    """获取首页文档列表（编辑过/浏览过/点赞/评论）"""
    document_service = DocumentHistoryService(db)
    temp_query = query_in.model_copy(update={"user_id": current_user.id})
    document_list = document_service.get_document_history_list(temp_query)
    return document_list