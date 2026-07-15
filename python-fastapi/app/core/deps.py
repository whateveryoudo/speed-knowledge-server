"""依赖注入"""

from fastapi import Depends, HTTPException, status, Query, Request, Header
from typing import Generator, Union, Optional
from app.db.session import SessionLocal
from sqlalchemy.orm.session import Session
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.models.user import User
from app.core.security import decode_access_token
from app.services.user_service import UserService
from app.models.knowledge import Knowledge
from app.models.document import Document
from app.services.document_service import DocumentService
from app.services.knowledge_service import KnowledgeService
from app.services.permission_service import PermissionService
from app.services.space_service import SpaceService
from app.models.space import Space
from app.services.team_service import TeamService
from app.core.redis_client import get_redis
import redis
from app.models.team import Team
from app.common.enums import (
    CollaborateResourceType,
    SpaceType,
    KnowledgeAbility,
    DocumentAbility,
)
from app.core.config import settings
from app.common.utils import get_space_subdomain


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
optional_bearer_scheme = HTTPBearer(auto_error=False)


_CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="无效的令牌，请重新登录",
    headers={"WWW-Authenticate": "Bearer"},
)


def _resolve_user_from_token(token: str, db: Session) -> User:
    """从access_token中解析用户(这里提取公共方法，多个地方复用)"""
    # 解密token
    payload = decode_access_token(token)

    if payload is None:
        raise _CREDENTIALS_EXCEPTION

    user_id = payload.get("sub")
    if user_id is None:
        raise _CREDENTIALS_EXCEPTION

    user = UserService(db).get_by_id(int(user_id))
    if user is None:
        raise _CREDENTIALS_EXCEPTION

    return user


def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(optional_bearer_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """_summary_: 获取当前用户(可选)"""
    if credentials is None:
        return None
    return _resolve_user_from_token(credentials.credentials, db)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """_summary_: 获取当前用户(鉴权)"""
    return _resolve_user_from_token(credentials.credentials, db)


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


class VertifyDocumentPermission:
    """验证文档权限（strict，走 ability，不认公开只读）"""

    def __init__(self, ability_key: Union[KnowledgeAbility, DocumentAbility]):
        self.ability_key = ability_key

    def __call__(
        self,
        identifier: str,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> Document:
        if not isinstance(self.ability_key, DocumentAbility):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文档权限校验能力类型不匹配",
            )
        return PermissionService(db).assert_document_ability(
            current_user.id, identifier, self.ability_key
        )


def get_document_or_403(
    identifier: str,
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
) -> Document:
    """获取文档或返回403(这里改成了直接使用PermissionService的assert_document_readable方法，不仅仅通过权限值判断，考虑了公开的场景)"""
    return PermissionService(db).assert_document_readable(
        current_user.id if current_user and current_user.id else None, identifier
    )


def get_knowledge_or_403(
    identifier: str,
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
) -> Knowledge:
    """获取知识库或返回403(这里改成了直接使用PermissionService的assert_knowledge_readable方法，不仅仅通过权限值判断，考虑了公开的场景)"""
    return PermissionService(db).assert_knowledge_readable(
        current_user.id if current_user and current_user.id else None, identifier
    )


class VertifyKnowledgePermission:
    """验证知识库权限"""

    def __init__(self, ability_key: Union[KnowledgeAbility, DocumentAbility]):
        self.ability_key = ability_key

    def __call__(
        self,
        identifier: str,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> Optional[Knowledge]:
        """验证资源权限"""
        return PermissionService(db).assert_knowledge_ability(
            current_user.id, identifier, self.ability_key
        )


# def vertify_knowledge_manage_permission(
#     identifier: str,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ) -> Knowledge:
#     """验证知识库管理权限"""
#     knowledge_service = KnowledgeService(db)
#     target_knowledge = knowledge_service.get_by_id_or_slug(identifier)
#     if not target_knowledge:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="知识库不存在"
#         )

#     permission_service = PermissionService(db)
#     if not permission_service.can_manage_knowledge(
#         current_user.id, target_knowledge.id
#     ):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN, detail="你无权管理此知识库"
#         )
#     return target_knowledge


def get_current_space(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取当前空间"""
    host = request.headers.get("host", "")
    space_service = SpaceService(db)
    space_domin = get_space_subdomain(host)
    if space_domin:
        space = space_service.get_space_by_domin(space_domin)
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


def verify_internal_token(
    x_internal_token: str = Header(..., description="服务间调用token"),
) -> None:
    """验证服务间调用token"""
    if x_internal_token != settings.INTERNAL_SERVICE_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的服务间调用token"
        )
    return True


def idempency_interceptor_key(
    request: Request,
    redis_client: redis.Redis = Depends(get_redis),
) -> str:
    """获取幂等性拦截器key"""
    idempency_key = request.headers.get("idempotency-key", "")
    if not idempency_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing Idempotency-Key"
        )
    router_key = f"idem:{request.method}:{request.path}:{idempency_key}"
    if redis_client.get(router_key):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Idempotency-Key already processed",
        )
    redis_client.set(router_key, "processing", nx=True, ex=60)
    try:
        yield router_key
        redis_client.set(router_key, "success", ex=5 * 60)
    except Exception as e:
        redis_client.delete(router_key)
        raise e
