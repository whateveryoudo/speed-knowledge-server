"""依赖注入"""

from fastapi import Depends, HTTPException, status, Query
from typing import Generator
from app.db.session import SessionLocal
from sqlalchemy.orm.session import Session
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.models.user import User
from app.core.security import decode_access_token
from app.services.user_service import UserService
from app.models.knowledge import Knowledge
from app.models.document import Document
from app.services.document_service import DocumentService
from app.models.knowledge_collaborator import KnowledgeCollaborator
from app.common.enums import KnowledgeCollaboratorStatus
from app.common.enums import KnowledgeCollaboratorRole
from app.schemas.knowledge import KnowledgeResponse
from app.services.knowledge_service import KnowledgeService
from app.services.knowledge_collaborator_service import KnowledgeCollaboratorService

def get_db() -> Generator:
    """_summary_: 获取数据库会话

    Yields:
        Generator: _description_
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


bearer_scheme = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """_summary_: 获取当前用户(鉴权)"""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的令牌，请重新登录",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    # 解密token
    payload = decode_access_token(token)

    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = UserService(db).get_by_id(int(user_id))
    if user is None:
        raise credentials_exception

    return user


# 用于获取查询参数中的用户（可以用在一些直接用url访问的）
def get_current_user_from_query(
    access_token: str = Query(..., description="access_token"),
    db: Session = Depends(get_db),
) -> User:
    """_summary_: 从查询参数中获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的令牌，请重新登录",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(access_token)
    if payload is None:
        raise credentials_exception
    user_id = payload.get("sub")
    user = UserService(db).get_by_id(int(user_id))
    if user is None:
        raise credentials_exception
    return user

def get_document_or_403(
    identifier: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Document:
    """获取文档或返回403"""
    document_service = DocumentService(db)
    document = document_service.get_by_id_or_slug(identifier, current_user.id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")
    if not document.is_public and document.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="你无权操作此文档")
    return document

def can_manage_knowledge(role: KnowledgeCollaboratorRole | None) -> bool:
    return role in [KnowledgeCollaboratorRole.ADMIN]

def can_edit_knowledge(role: KnowledgeCollaboratorRole | None) -> bool:
    return role in [KnowledgeCollaboratorRole.ADMIN, KnowledgeCollaboratorRole.EDITOR]

def can_read_knowledge(role: KnowledgeCollaboratorRole | None, is_public: bool) -> bool:
    return is_public or role is not None

def get_knowledge_or_403(identifier: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> KnowledgeResponse:
    """获取知识库或返回403"""
    knowledge_service = KnowledgeService(db)
    target_knowledge = knowledge_service.get_by_id_or_slug(identifier)
    if not target_knowledge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="知识库不存在")
    
    collaborator_service = KnowledgeCollaboratorService(db)
    role = collaborator_service.get_user_role_in_knowledge(current_user.id, target_knowledge.id)
    if not can_read_knowledge(role, target_knowledge.is_public):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="你无权访问此知识库")
    return target_knowledge

def vertify_knowledge_manage_permission(identifier: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> KnowledgeResponse:
    """验证知识库管理权限"""
    knowledge_service = KnowledgeService(db)
    target_knowledge = knowledge_service.get_by_id_or_slug(identifier)
    if not target_knowledge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="知识库不存在")
    
    collaborator_service = KnowledgeCollaboratorService(db)
    role = collaborator_service.get_user_role_in_knowledge(current_user.id, target_knowledge.id)
    if not can_manage_knowledge(role):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="你无权管理此知识库")
    return target_knowledge