from app.models.document_view_history import DocumentViewHistory
from sqlalchemy.orm import Session
from app.schemas.document_view_history import (
    DocumentViewHistoryCreate,
)
from datetime import datetime


class DocumentViewHistoryService:
    """文档历史浏览服务"""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self, document_view_history_in: DocumentViewHistoryCreate
    ) -> DocumentViewHistory:
        """创建文档浏览历史"""
        # 先通过document_id和user_id查询是否存在
        document_view_history = (
            self.db.query(DocumentViewHistory)
            .filter(
                DocumentViewHistory.document_id == document_view_history_in.document_id,
                DocumentViewHistory.viewed_user_id == document_view_history_in.viewed_user_id,
            )
            .first()
        )
        if document_view_history:
            # 更新下最新的时间
            document_view_history.viewed_datetime = datetime.now()
        else:
            # 增加一条新的记录
            document_view_history = DocumentViewHistory(
                document_id=document_view_history_in.document_id,
                viewed_user_id=document_view_history_in.viewed_user_id,
                viewed_datetime=document_view_history_in.viewed_datetime,
            )
            self.db.add(document_view_history)
        self.db.commit()
        self.db.refresh(document_view_history)
        return document_view_history
