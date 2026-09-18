"""文档端点"""

from fastapi import (
    APIRouter,
    status,
    Depends,
    HTTPException,
    Query,
    Form,
    UploadFile,
    File,
    Request,
)
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm.session import Session
from typing import List
from app.schemas.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentRouteContext,
    DocumentExportRequest,
    DocumentVisibilityUpdate,
)
from app.core.deps import (
    get_db,
    VerifyDocumentPermission,
    VerifyKnowledgePermission,
    get_current_user,
    get_optional_current_user,
    get_document_or_403,
    get_knowledge_or_403,
)
from app.models.user import User
from app.services.document_service import DocumentService
from app.services.document_node_service import DocumentNodeService
from app.models.document import Document
from app.services.document_view_history import DocumentViewHistoryService
from app.schemas.document_view_history import DocumentViewHistoryCreate
from app.schemas.document_node import (
    DocumentNodeResponse,
    DragDocumentNodeParams,
    CatalogNodeCreate,
    DocumentNodeUpdate,
)
from datetime import datetime
from app.services.collect_service import CollectService
from app.common.enums import (
    DocumentImportFormat,
    DocumentType,
    DocumentAbility,
    CollectTargetType,
    KnowledgeAbility,
)
from app.schemas.user import UserResponse
from app.models.knowledge import Knowledge

router = APIRouter()
node_router = APIRouter()


@router.post(
    "/docs", response_model=DocumentNodeResponse, status_code=status.HTTP_201_CREATED
)
async def create_document(
    document_in: DocumentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentNodeResponse:
    """创建文档"""
    document_service = DocumentService(db)

    document_data = document_in.model_copy(update={"user_id": current_user.id})
    created_document_node = document_service.create(document_data)

    return created_document_node


@router.post("/{space_id}/default/docs", response_model=DocumentRouteContext)
async def create_default_document(
    space_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentRouteContext:
    """创建默认文档(这里会先创建一个默认知识库，然后创建一个默认文档)"""
    from app.services.knowledge_service import KnowledgeService
    from app.schemas.knowledge import KnowledgeCreate

    knowledge_service = KnowledgeService(db)
    knowledge = knowledge_service.create_knowledge_for_quick_document(
        KnowledgeCreate(
            creator_id=current_user.id,
            name="默认知识库",
            space_id=space_id,
            team_id=None,
        )
    )
    document_service = DocumentService(db)
    return document_service.create_quick_document(
        DocumentCreate(
            name="无标题文档",
            knowledge_id=knowledge.id,
            type=DocumentType.WORD,
            user_id=current_user.id,
            parent_id=None,
        )
    )


@router.get("/{identifier}/document/list", response_model=List[DocumentResponse])
async def get_document_list_by_knowledge_id(
    knowledge: Knowledge = Depends(get_knowledge_or_403),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[DocumentResponse]:
    """获取知识库下的文档列表"""
    document_service = DocumentService(db)
    document_list = document_service.get_list_by_knowledge_id(
        knowledge_id=knowledge.id, user_id=current_user.id
    )
    return document_list


@router.post(
    "/{identifier}/import",
    response_model=DocumentNodeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def import_document(
    request: Request,
    parent_id: str | None = Form(None),
    file: UploadFile = File(...),
    format: DocumentImportFormat = Form(...),
    knowledge: Knowledge = Depends(
        VerifyKnowledgePermission(KnowledgeAbility.CREATE_DOCUMENT)
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentNodeResponse:
    """导入文档（返回文档树节点，与新建文档一致）"""
    document_service = DocumentService(db)
    file_bytes = await file.read()
    file_name = file.filename
    return document_service.import_document(
        user_id=current_user.id,
        knowledge_id=knowledge.id,
        parent_id=parent_id,
        file_bytes=file_bytes,
        file_name=file_name or "未命名.docx",
        content_type=file.content_type or "application/octet-stream",
        format=format,
    )


@router.post("/{identifier}/export", response_model=None)
async def export_document(
    body: DocumentExportRequest,
    document: Document = Depends(VerifyDocumentPermission(DocumentAbility.DOC_EXPORT)),
    db: Session = Depends(get_db),
):
    """导出文档"""
    document_service = DocumentService(db)
    return await run_in_threadpool(
        document_service.export_document, document.id, body.format
    )


@router.get("/{identifier}", response_model=DocumentResponse)
async def get_document_detail(
    document: Document = Depends(get_document_or_403),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> DocumentResponse:
    """通过id或短链获取文档详情"""
    if current_user and current_user.id:
        collect_service = CollectService(db)
        collected_record = collect_service.check_is_collected(
            user_id=current_user.id,
            target_type=CollectTargetType.DOCUMENT,
            target_id=document.id,
        )
    else:
        collected_record = None
    return DocumentResponse.model_validate(document).model_copy(
        update={"has_collected": bool(collected_record)}
    )


@router.put("/{identifier}", response_model=DocumentResponse)
async def update_document(
    identifier: str,
    document_in: DocumentUpdate,
    document: Document = Depends(VerifyDocumentPermission(DocumentAbility.DOC_EDIT)),
    db: Session = Depends(get_db),
) -> Document:
    """更新文档"""
    document_service = DocumentService(db)

    updated_document = document_service.update_by_id_or_slug(identifier, document_in)
    return updated_document


@router.get("/content/{identifier}", response_model=str)
async def get_document_content(
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
    document: Document = Depends(get_document_or_403),
) -> str:
    """获取文档内容(这里是json数据)"""
    document_service = DocumentService(db)
    document_content = document_service.get_content(document.id)
    # 更新浏览历史记录(游客不更新)
    if current_user and current_user.id:
        document_view_history_service = DocumentViewHistoryService(db)
        document_view_history_service.create(
            DocumentViewHistoryCreate(
                document_id=document.id,
                viewed_user_id=current_user.id,
                viewed_datetime=datetime.now(),
            )
        )
    return document_content


@router.delete("/{identifier}", response_model=None)
async def delete_document(
    document: Document = Depends(VerifyDocumentPermission(DocumentAbility.DOC_DELETE)),
    db: Session = Depends(get_db),
) -> None:
    """删除文档"""
    document_service = DocumentService(db)
    return document_service.delete_by_id_or_slug(document.id)


@router.get("/{identifier}/context-users", response_model=List[UserResponse])
async def get_context_users(
    keyword: str | None = Query(None),
    document: Document = Depends(VerifyDocumentPermission(DocumentAbility.DOC_READ)),
    db: Session = Depends(get_db),
) -> List[UserResponse]:
    """获取文档上下文用户列表"""
    document_service = DocumentService(db)
    return document_service.get_context_users(document_id=document.id, keyword=keyword)


@router.patch("/{identifier}/visibility", response_model=bool)
async def update_document_visibility(
    document_visibility_in: DocumentVisibilityUpdate,
    document: Document = Depends(VerifyDocumentPermission(DocumentAbility.DOC_SHARE)),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> bool:
    """更新文档可见范围"""
    document_service = DocumentService(db)
    return document_service.update_visibility(
        document=document,
        visibility=document_visibility_in.visibility,
        operator_id=current_user.id,
    )


@node_router.post(
    "/catalog_nodes",
    response_model=DocumentNodeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_catalog_node(
    document_node_in: CatalogNodeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentNodeResponse:
    """创建目录节点"""
    document_node_service = DocumentNodeService(db)
    # 这里直接调用节点服务，不调用文档服务创建文档
    created_document_node = document_node_service.create_catalog_node(
        operator_id=current_user.id,
        knowledge_id=document_node_in.knowledge_id,
        name=document_node_in.name,
        parent_id=document_node_in.parent_id,
    )
    return created_document_node


@node_router.put("/drag", response_model=None)
async def drag_document(
    drag_document_in: DragDocumentNodeParams,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """拖拽文档节点（这里放到前面优先匹配）"""
    document_node_service = DocumentNodeService(db)
    return document_node_service.drag_document(
        operator_id=current_user.id, drag_document_in=drag_document_in
    )


@node_router.delete("/{node_id}", response_model=None)
async def delete_document_node(
    node_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """删除文档节点（1.DOC软删；2.双向链表更新；3.递归删除子项）"""
    document_node_service = DocumentNodeService(db)
    return document_node_service.delete_node(
        operator_id=current_user.id, node_id=node_id
    )


@node_router.put("/{node_id}", response_model=None)
async def update_document_node(
    node_id: str,
    document_node_in: DocumentNodeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """更新文档节点"""
    document_node_service = DocumentNodeService(db)
    return document_node_service.update_node(
        operator_id=current_user.id, node_id=node_id, update_in=document_node_in
    )
