"""文档端点"""

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm.session import Session
from typing import List
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse
from app.core.deps import get_db, get_current_user, get_document_or_403
from app.models.user import User
from app.services.document_service import DocumentService
from app.services.document_node_service import DocumentNodeService
from app.models.document import Document
from app.services.document_view_history import DocumentViewHistoryService
from app.schemas.document_view_history import DocumentViewHistoryCreate
from app.schemas.document import DragDocumentNodeParams
from datetime import datetime
from app.services.collect_service import CollectService
from app.common.enums import CollectResourceType

router = APIRouter()
node_router = APIRouter()


@router.post("/docs", response_model=str, status_code=status.HTTP_201_CREATED)
async def create_document(
    document_in: DocumentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> str:
    """创建文档"""
    document_service = DocumentService(db)

    document_data = document_in.model_copy(update={"user_id": current_user.id})
    created_document = document_service.create(document_data)

    return created_document.slug


@router.post("/catalog_nodes", response_model=str, status_code=status.HTTP_201_CREATED)
async def create_catalog_node(
    document_in: DocumentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> str:
    """创建目录节点"""
    document_node_service = DocumentNodeService(db)
    # 这里直接调用节点服务，不调用文档服务创建文档
    created_document = document_node_service.create_node(
        document_in, document_in.parent_id
    )
    return created_document.id


@router.get("/{knowledge_id}/document/list", response_model=List[DocumentResponse])
async def get_document_list_by_knowledge_id(
    knowledge_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[DocumentResponse]:
    """获取知识库下的文档列表"""
    document_service = DocumentService(db)
    document_list = document_service.get_list_by_knowledge_id(knowledge_id)
    return document_list


@router.get("/{identifier}", response_model=DocumentResponse)
async def get_document_detail(
    document: Document = Depends(get_document_or_403),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentResponse:
    """通过id或短链获取文档详情"""
    collect_service = CollectService(db)
    collected_record = collect_service.check_is_collected(
        current_user.id, document.id, CollectResourceType.DOCUMENT
    )
    return DocumentResponse.model_validate(document).model_copy(
        update={"has_collected": collected_record is not None}
    )


@node_router.put("/drag", response_model=None)
async def drag_document(
    drag_document_in: DragDocumentNodeParams,
    db: Session = Depends(get_db),
) -> None:
    """拖拽文档节点（这里放到前面优先匹配）"""
    print(drag_document_in)
    document_node_service = DocumentNodeService(db)
    return document_node_service.drag_document(drag_document_in)


@router.put("/{identifier}", response_model=DocumentResponse)
async def update_document(
    identifier: str,
    document_in: DocumentUpdate,
    document: Document = Depends(get_document_or_403),
    db: Session = Depends(get_db),
) -> Document:
    """更新文档"""
    document_service = DocumentService(db)

    updated_document = document_service.update_by_id_or_slug(identifier, document_in)
    return updated_document


@router.get("/content/{document_id}", response_model=str)
async def get_document_content(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> str:
    """获取文档内容(这里是json数据)"""
    document_service = DocumentService(db)
    document_content = document_service.get_content(document_id)
    # 更新浏览历史记录
    document_view_history_service = DocumentViewHistoryService(db)
    document_view_history_service.create(
        DocumentViewHistoryCreate(
            document_id=document_id,
            viewed_user_id=current_user.id,
            viewed_datetime=datetime.now(),
        )
    )
    return document_content


@router.delete("/{identifier}", response_model=None)
async def delete_document(
    identifier: str,
    document: Document = Depends(get_document_or_403),
    db: Session = Depends(get_db),
) -> None:
    """删除文档"""
    document_service = DocumentService(db)
    return document_service.delete_by_id_or_slug(identifier)
