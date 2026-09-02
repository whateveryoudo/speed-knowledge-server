from app.models.document_view_history import DocumentViewHistory
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.document_history import (
    DocumentHistoryQuery,
    DocumentHistoryResponse,
)
from app.common.pagination import paginate_response, paginate_after_fetch
from app.schemas.response import PaginationQuery, PaginationResponse
from sqlalchemy.orm import joinedload
from app.models import (
    Knowledge,
    Document,
)
from app.services.collect_service import CollectService
from app.common.enums import (
    DocumentHistoryType,
    ResourceType,
    DocumentCreatorScope,
    CollectTargetType,
)
from app.models.document_edit_history import DocumentEditHistory
from app.services.permission_service import PermissionService


class DocumentHistoryService:
    """文档历史服务"""

    def __init__(self, db: Session):
        self.db = db
        self.permission_service = PermissionService(db)

    def get_document_history_list(
        self, *, user_id: int, query_in: DocumentHistoryQuery
    ) -> PaginationResponse[DocumentHistoryResponse]:
        """获取文档历史列表"""
        collection_service = CollectService(self.db)

        if query_in.history_type == DocumentHistoryType.VIEW:
            model = DocumentViewHistory
            user_id_field = DocumentViewHistory.viewed_user_id
            history_datetime_field = DocumentViewHistory.viewed_datetime
        elif query_in.history_type == DocumentHistoryType.EDIT:
            model = DocumentEditHistory
            user_id_field = DocumentEditHistory.edited_user_id
            history_datetime_field = DocumentEditHistory.edited_datetime
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的历史列表类型: {query_in.history_type.value}",
            )

        query = (
            self.db.query(model)
            .join(Document, model.document_id == Document.id)
            .join(Knowledge, Document.knowledge_id == Knowledge.id)
            .filter(
                user_id_field == user_id,
                Knowledge.deleted_at.is_(None),
                Document.deleted_at.is_(None),
            )
            .options(
                joinedload(model.document),
                # 预加载知识库信息（通过文档关联）
                joinedload(model.document)
                .joinedload(Document.knowledge)
                .joinedload(Knowledge.team),
                # 预加载文档创建者信息
                joinedload(model.document).joinedload(Document.user),
            )
        )
        filter_conditions = []

        if query_in.doc_name:
            filter_conditions.append(Document.name.like(f"%{query_in.doc_name}%"))
        if query_in.doc_belong_knowledge_id:
            filter_conditions.append(
                Document.knowledge_id == query_in.doc_belong_knowledge_id
            )
        if query_in.doc_type:
            filter_conditions.append(Document.type == query_in.doc_type)
        if query_in.doc_creator_scope == DocumentCreatorScope.MINE:
            filter_conditions.append(Document.user_id == user_id)
        if filter_conditions:
            query = query.filter(*filter_conditions)

        # 增加可读过滤
        candidate_items = query.order_by(
            history_datetime_field.desc(),
            model.created_at.desc(),
        ).all()

        documents_by_id = {
            item.document.id: item.document
            for item in candidate_items
            if item.document is not None
        }
        readability_by_id = (
            self.permission_service.resolve_multiple_document_readabilities(
                user_id=user_id, documents=list(documents_by_id.values())
            )
        )

        readable_items = [
            item
            for item in candidate_items
            if item.document is not None
            and readability_by_id.get(item.document.id, False)
        ]

        pagination_query = PaginationQuery(
            page=query_in.page, page_size=query_in.page_size
        )

        page_items = readable_items[
            pagination_query.skip : pagination_query.skip + pagination_query.limit
        ]

        # 进行分页查询
        items, total, has_more = paginate_after_fetch(
            items=page_items,
            total=len(readable_items),
            pagination_query=pagination_query,
        )  # 返回数据和总条数
        # 内容组合
        response_items: list[DocumentHistoryResponse] = []
        # 调整为批量查询
        collected_document_ids = collection_service.get_collected_target_ids(
            user_id=user_id,
            target_type=CollectTargetType.DOCUMENT,
            target_ids=[item.document_id for item in items],
        )
        for item in items:
            doc_creator = (
                item.document.user.nickname or item.document.user.username
                if item.document.user
                else ""
            )

            if query_in.history_type == DocumentHistoryType.VIEW:
                update_datetime = item.viewed_datetime
            else:
                update_datetime = item.edited_datetime
            knowledge = item.document.knowledge
            if not knowledge:
                continue
            team = knowledge.team if knowledge else None
            response_item = DocumentHistoryResponse(
                id=item.id,
                doc_id=item.document_id,
                update_datetime=update_datetime,
                doc_creator=doc_creator,
                doc_belong_space_id=knowledge.space_id,
                doc_belong_team_slug=team.slug if team else None,
                doc_belong_team_name=team.name if team else None,
                doc_belong_knowledge_name=(knowledge.name if knowledge else ""),
                doc_belong_knowledge_id=knowledge.id,
                doc_belong_knowledge_slug=knowledge.slug,
                doc_name=item.document.name,
                doc_type=item.document.type,
                doc_slug=item.document.slug,
                doc_is_collected=item.document_id in collected_document_ids,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            response_items.append(response_item)
        return paginate_response(response_items, total, has_more, query_in)
