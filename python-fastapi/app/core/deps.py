"""依赖注入"""

from fastapi import Depends, HTTPException, status
from typing import Generator
from app.db.session import SessionLocal
from sqlalchemy.orm.session import Session
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.models.user import User
from app.core.security import decode_access_token
from app.services.user_service import UserService
from app.models.knowledge import Knowledge


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


def vertify_knowledge_owner(
    knowledge_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Knowledge:
    """知识库鉴权校验

    Args:
        knowledge_id (int): 知识库id
        user (User, optional): _description_. Defaults to Depends(get_current_user).
        db (Session, optional): _description_. Defaults to Depends(get_db).
    """
    from app.services.knowledge_service import KnowledgeService

    knowledge_service = KnowledgeService(db)
    target_knowledge = knowledge_service.get_by_id(knowledge_id)
    if not target_knowledge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="知识库不存在"
        )
    if str(current_user.id) == str(target_knowledge.id):
        return target_knowledge
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="你无权操作此知识库"
    )
