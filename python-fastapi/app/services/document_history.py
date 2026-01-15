from app.models.document_view_history import DocumentViewHistory
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.document_history import (
    DocumentHistoryQuery,
    DocumentHistoryResponse,
)
from app.common.pagination import paginate_query, paginate_response
from app.schemas.response import PaginationQuery, PaginationResponse
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from app.models.document import Document
from app.services.collect_service import CollectService
from app.common.enums import CollectResourceType, DocumentHistoryType
from app.models.document_edit_history import DocumentEditHistory



class DocumentHistoryService:
    """文档历史服务"""

    def __init__(self, db: Session):
        self.db = db
    def get_document_history_list(
        self, query_in: DocumentHistoryQuery
    ) -> PaginationResponse[DocumentHistoryResponse]:
        """获取文档历史列表"""
        collection_service = CollectService(self.db)

        if query_in.history_type == DocumentHistoryType.VIEW:
            model = DocumentViewHistory
            user_id_field = DocumentViewHistory.viewed_user_id
        elif query_in.history_type == DocumentHistoryType.EDIT:
            model = DocumentEditHistory
            user_id_field = DocumentEditHistory.edited_user_id
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的历史列表类型: {query_in.history_type.value}",
            )
      
        query = (
            self.db.query(model)
            .join(Document, model.document_id == Document.id)
            .filter(user_id_field == query_in.user_id, Document.deleted_at.is_(None))
            .options(
                joinedload(model.document),
                # 预加载知识库信息（通过文档关联）
                joinedload(model.document).joinedload(
                    Document.knowledge
                ),
                # 预加载文档创建者信息
                joinedload(model.document).joinedload(
                    Document.user
                ),
            )
        )
        filter_conditions = []

        if query_in.doc_name:
            filter_conditions.append(
                model.document.name.like(f"%{query_in.doc_name}%")
            )
        if query_in.doc_belong_knowledge_id:
            filter_conditions.append(
                model.document.knowledge.id == query_in.doc_belong_knowledge_id
            )
        if query_in.doc_type:
            filter_conditions.append(
                model.document.type == query_in.doc_type
            )
        if query_in.doc_creator:
            filter_conditions.append(
                model.document.creator == query_in.doc_creator
            )
        if filter_conditions:
            query = query.filter(*filter_conditions)

        # 进行分页查询
        items, total = paginate_query(
            query, PaginationQuery(page=query_in.page, page_size=query_in.page_size)
        )  # 返回数据和总条数
        # 内容组合
        response_items = []
        for item in items:
            doc_creator = (
                item.document.user.nickname or item.document.user.username
                if item.document.user
                else ""
            )
            # 查询文档是否被收藏
            collected_row = collection_service.check_is_collected(
                query_in.user_id, item.document_id, CollectResourceType.DOCUMENT
            )
            if query_in.history_type == DocumentHistoryType.VIEW:
                update_datetime = item.viewed_datetime
            else:
                update_datetime = item.edited_datetime
            response_item = DocumentHistoryResponse(
                id=item.id,
                doc_id=item.document_id,
                update_datetime=update_datetime,
                doc_creator=doc_creator,
                doc_belong_knowledge_name=(
                    item.document.knowledge.name
                    if item.document.knowledge
                    else ""
                ),
                doc_belong_knowledge_slug=item.document.knowledge.slug,
                doc_name=item.document.name,
                doc_type=item.document.type,
                doc_slug=item.document.slug,
                doc_is_collected=collected_row is not None,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            response_items.append(response_item)
        return paginate_response(response_items, total, query_in)
                
