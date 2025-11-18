"""知识库端点"""

from fastapi import APIRouter, status, Depends
from sqlalchemy.orm.session import Session
from typing import List
from app.schemas.knowledge import KnowledgeCreate, KnowledgeResponse
from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.services.knowledge_service import KnowledgeService

router = APIRouter()


@router.post("/", response_model=int, status_code=status.HTTP_201_CREATED)
async def create_knowledge(
    knowledge_in: KnowledgeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> int:
    """创建知识库"""
    knowledge_service = KnowledgeService(db)

    knowledge_data = knowledge_in.model_copy(update={"user_id": current_user.id})
    created_knowledge = knowledge_service.create(knowledge_data)
    return created_knowledge.id


@router.get("/list", response_model=List[KnowledgeResponse])
async def get_knowledge_list(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> List[KnowledgeResponse]:
    """获取知识库列表"""
    knowledge_service = KnowledgeService(db)
    knowledge_list = knowledge_service.get_list_by_user_id(current_user.id)
    return knowledge_list
