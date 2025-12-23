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

router = APIRouter()


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
) -> DocumentResponse:
    """通过id或短链获取文档详情"""
    return document


@router.put("/{identifier}", response_model=DocumentResponse)
async def update_document(
    document_in: DocumentUpdate,
    document: Document = Depends(get_document_or_403),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    """更新文档"""
    if document_in.name is not None:
        document.name = document_in.name
    if document_in.slug is not None:
        document.slug = document_in.slug
    document_service = DocumentService(db)
    updated_document = document_service.update_by_id_or_slug(document)
    return updated_document
