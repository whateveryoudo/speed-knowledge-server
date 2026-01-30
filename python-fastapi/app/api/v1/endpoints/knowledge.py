"""知识库端点"""

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm.session import Session
from typing import List, Optional
from app.schemas.knowledge import (
    KnowledgeCreate,
    KnowledgeResponse,
    KnowledgeIndexPageResponse,
    KnowledgeFullResponse,
)
from app.core.deps import (
    get_db,
    get_current_user,
    get_knowledge_or_403,
    get_current_team,
)
from app.models.user import User
from app.models.knowledge import Knowledge
from app.models.team import Team
from app.services.knowledge_service import KnowledgeService
from app.services.knowledge_group_service import KnowledgeGroupService
from app.services.document_node_service import DocumentNodeService
from app.schemas.document_node import DocumentNodeResponse
from app.services.knowledge_daily_stats_service import KnowledgeDailyStatsService
from app.schemas.knowledge_daily_stats import KnowledgeDailyStatsResponse
from app.services.collect_service import CollectService

from app.common.enums import (
    CollectResourceType,
)
from app.schemas.knowledge_group import (
    KnowledgeGroupUpdate,
    KnowledgeGroupResponse,
    KnowledgeGroupCreate,
)

router = APIRouter()


@router.post("/", response_model=str, status_code=status.HTTP_201_CREATED)
async def create_knowledge(
    knowledge_in: KnowledgeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> str:
    """创建知识库"""
    knowledge_service = KnowledgeService(db)

    knowledge_data = knowledge_in.model_copy(update={"user_id": current_user.id})
    created_knowledge = knowledge_service.create(knowledge_data)
    return created_knowledge.slug


@router.get("/list", response_model=List[KnowledgeResponse])
async def get_knowledge_list(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> List[KnowledgeResponse]:
    """获取知识库列表"""
    knowledge_service = KnowledgeService(db)
    knowledge_list = knowledge_service.get_list_by_user_id(current_user.id)
    return knowledge_list


@router.get("/{identifier}", response_model=KnowledgeResponse)
async def get_knowledge_detail(
    knowledge: Knowledge = Depends(get_knowledge_or_403),
) -> Knowledge:
    """通过短链/id获取知识库详情"""
    return knowledge


@router.get("/{identifier}/index-page", response_model=KnowledgeIndexPageResponse)
async def get_knowledge_index_page(
    knowledge: Knowledge = Depends(get_knowledge_or_403),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> KnowledgeIndexPageResponse:
    """获取知识库的首页信息"""
    knowledge_daily_stats_service = KnowledgeDailyStatsService(db)
    collect_service = CollectService(db)
    if knowledge and knowledge.id:
        knowledge_index_page_schema = KnowledgeFullResponse.model_validate(knowledge)
        knowledge_daily_stats = (
            knowledge_daily_stats_service.get_daily_stats_by_knowledge_id(knowledge.id)
        )
        knowledge_daily_stats_schema = (
            KnowledgeDailyStatsResponse.model_validate(knowledge_daily_stats)
            if knowledge_daily_stats
            else None
        )
        collected_record = collect_service.check_is_collected(
            current_user.id, knowledge.id, CollectResourceType.KNOWLEDGE
        )
        # 合并一些属性
        return KnowledgeIndexPageResponse(
            **knowledge_index_page_schema.model_dump(),
            word_count=(
                knowledge_daily_stats_schema.word_count
                if knowledge_daily_stats_schema
                else 0
            ),
            has_collected=collected_record is not None,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="知识库不存在"
        )


# 这里是直接创建一个默认的分组，不需要传入任何参数
@router.post("/group/create", response_model=str, status_code=status.HTTP_201_CREATED)
async def create_knowledge_group(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> int:
    """创建知识库分组"""
    knowledge_group_service = KnowledgeGroupService(db)
    group_length = len(knowledge_group_service.get_list_by_user_id(current_user.id))
    knowledge_group_data = KnowledgeGroupCreate(
        user_id=current_user.id,
        group_name="新建分组",
        order_index=group_length,
        is_default=False,
    )
    created_knowledge_group = knowledge_group_service.create(knowledge_group_data)
    return created_knowledge_group.id


@router.put(
    "/group/update/{group_id}", response_model=None, status_code=status.HTTP_200_OK
)
async def update_knowledge_group(
    group_id: str,
    knowledge_group_in: KnowledgeGroupUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """更新知识库分组"""
    knowledge_group_service = KnowledgeGroupService(db)
    knowledge_group_service.update(group_id, knowledge_group_in)


@router.get("/group/list", response_model=List[KnowledgeGroupResponse])
async def get_knowledge_group_list(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> List[KnowledgeGroupResponse]:
    """获取知识库分组列表"""
    knowledge_group_service = KnowledgeGroupService(db)
    knowledge_group_list = knowledge_group_service.get_list_by_user_id(current_user.id)
    return knowledge_group_list


@router.get("/{knowledge_id}/document/tree", response_model=List[DocumentNodeResponse])
async def get_document_tree(
    knowledge_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[DocumentNodeResponse]:
    """获取知识库的文档树"""
    document_tree_service = DocumentNodeService(db)
    document_tree = document_tree_service.get_document_tree_nodes(knowledge_id)
    print("取到了文档树", document_tree)
    return document_tree
