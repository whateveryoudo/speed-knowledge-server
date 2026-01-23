"""依赖注入"""

from fastapi import Depends, HTTPException, status, Query, Request
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
from app.services.knowledge_service import KnowledgeService
from app.services.permission_service import PermissionService
from app.services.knowledge_collaborator_service import KnowledgeCollaboratorService
from app.services.space_service import SpaceService
from app.models.space import Space
from app.services.team_service import TeamService
from app.models.team import Team
from app.common.enums import SpaceType


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
    document = document_service.get_by_id_or_slug(identifier)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")
    
    permission_service = PermissionService(db)
    if not permission_service.can_read_document(current_user.id, document):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="你无权访问此文档"
        )
    return document


def get_knowledge_or_403(
    identifier: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Knowledge:
    """获取知识库或返回403"""
    knowledge_service = KnowledgeService(db)
    target_knowledge = knowledge_service.get_by_id_or_slug(identifier)
    if not target_knowledge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="知识库不存在"
        )

    permission_service = PermissionService(db)
    if not permission_service.can_read_knowledge(
        current_user.id, target_knowledge.id, target_knowledge.is_public
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="你无权访问此知识库"
        )
    return target_knowledge


def vertify_knowledge_manage_permission(
    identifier: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Knowledge:
    """验证知识库管理权限"""
    knowledge_service = KnowledgeService(db)
    target_knowledge = knowledge_service.get_by_id_or_slug(identifier)
    if not target_knowledge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="知识库不存在"
        )

    permission_service = PermissionService(db)
    if not permission_service.can_manage_knowledge(
        current_user.id, target_knowledge.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="你无权管理此知识库"
        )
    return target_knowledge


def get_current_space(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取当前空间"""
    host = request.headers.get("host", "").split(";")[0]
    parts = host.split(".")
    space_service = SpaceService(db)
    if len(parts) >= 3 and parts[0] not in {"localhost"}:
        space_domin = parts[0]
        space = space_service.get_by_domin(space_domin)
        if not space:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="空间不存在"
            )
        return space
    # 当前用户的个人空间
    space = (
        space_service.get_active_query()
        .filter(Space.owner_id == current_user.id, Space.type == SpaceType.PERSONAL)
        .first()
    )
    if not space:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="空间不存在")
    return space


def get_current_team(
    space: Space = Depends(get_current_space),
    db: Session = Depends(get_db),
):
    """获取当前团队"""
    team_service = TeamService(db)
    team = (
        team_service.get_active_query()
        .filter(Team.space_id == space.id, Team.is_default == True)
        .first()
    )
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="团队不存在")
    return team
