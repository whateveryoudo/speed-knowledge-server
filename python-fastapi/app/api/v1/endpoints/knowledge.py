"""知识库端点"""

from typing import List

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm.session import Session
from app.schemas.response import PaginationResponse
from app.schemas.knowledge import (
    KnowledgeCreate,
    KnowledgeResponse,
    KnowledgeIndexPageResponse,
    KnowledgeFullResponse,
    KnowledgeListQuery,
    KnowledgeListMineQuery,
)
from app.core.deps import (
    get_db,
    get_current_user,
    VertifyKnowledgePermission,
    get_knowledge_or_403,
    get_optional_current_user,
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
from app.services.permission_service import PermissionService
from app.services.knowledge_common_pin_service import KnowledgeCommonPinService
from app.schemas.knowledge_common_pin import KnowledgeCommonPinResponse

from app.common.enums import (
    CollectResourceType,
    CollaborateResourceType,
    KnowledgeAbility,
)
from app.schemas.knowledge_group import (
    KnowledgeGroupUpdateBody,
    KnowledgeGroupResponse,
    KnowledgeGroupCreate,
)
from app.schemas.knowledge_group_relation import KnowledgeGroupRelationMoveBody
from app.services.knowledge_group_relation_service import KnowledgeGroupRelationService
from app.common.utils import next_order_index
from app.models.knowledge_group import KnowledgeGroup
from app.services.collaborator_service import CollaboratorService

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


@router.post("/list", response_model=PaginationResponse)
async def get_knowledge_list(
    query_in: KnowledgeListQuery,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PaginationResponse:
    """获取知识库列表(这里主要是用于 知识库列表区分（我的/被邀请的）)"""
    knowledge_service = KnowledgeService(db)

    knowledge_list = knowledge_service.get_list_by_user_id(
        query_in.model_copy(update={"user_id": current_user.id})
    )
    return knowledge_list


@router.put(
    "/{identifier}/toggle-public", response_model=bool, status_code=status.HTTP_200_OK
)
async def toggle_knowledge_public(
    identifier: str,
    knowledge: Knowledge = Depends(
        VertifyKnowledgePermission(KnowledgeAbility.MODIFY_BOOK_PERMISSION)
    ),
    db: Session = Depends(get_db),
) -> bool:
    """切换知识库公开状态"""
    knowledge_service = KnowledgeService(db)
    return knowledge_service.toggle_public(identifier)


@router.post("/mine/list", response_model=PaginationResponse)
async def get_knowledge_list_mine(
    query_in: KnowledgeListMineQuery,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PaginationResponse:
    """获取我的知识库列表(主要是用于支持按照某些条件过滤)"""
    knowledge_service = KnowledgeService(db)
    return knowledge_service.get_list_mine(
        query_in.model_copy(update={"user_id": current_user.id})
    )


@router.get("/{identifier}", response_model=KnowledgeResponse)
async def get_knowledge_detail(
    current_user: User | None = Depends(get_optional_current_user),
    knowledge: Knowledge = Depends(get_knowledge_or_403),
    db: Session = Depends(get_db),
) -> Knowledge:
    """通过短链/id获取知识库详情"""
    knowledge_service = KnowledgeService(db)
    if current_user is None:
        # 支持游客访问知识库详情
        return knowledge_service.to_wrap_knowledge_response_for_guest(knowledge)
    # 同时追加当前用户的能力集合
    return knowledge_service.to_wrap_knowledge_response(knowledge, current_user.id)


@router.get("/{identifier}/index-page", response_model=KnowledgeIndexPageResponse)
async def get_knowledge_index_page(
    knowledge: Knowledge = Depends(get_knowledge_or_403),
    current_user: User | None = Depends(get_optional_current_user),
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
        if current_user and current_user.id:
            collected_record = collect_service.check_is_collected(
                current_user.id, knowledge.id, CollectResourceType.KNOWLEDGE
            )
        else:
            collected_record = None
        # 合并一些属性
        return KnowledgeIndexPageResponse(
            **knowledge_index_page_schema.model_dump(),
            word_count=(
                knowledge_daily_stats_schema.word_count
                if knowledge_daily_stats_schema
                else 0
            ),
            has_collected=bool(collected_record),
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
    order_index = next_order_index(db, KnowledgeGroup, user_id=current_user.id)
    knowledge_group_data = KnowledgeGroupCreate(
        user_id=current_user.id,
        group_name="新建分组",
        order_index=order_index,
        is_default=False,
    )
    created_knowledge_group = knowledge_group_service.create(knowledge_group_data)
    return created_knowledge_group


@router.put(
    "/group/update/{group_id}", response_model=None, status_code=status.HTTP_200_OK
)
async def update_knowledge_group(
    group_id: str,
    knowledge_group_in: KnowledgeGroupUpdateBody,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """更新知识库分组"""
    knowledge_group_service = KnowledgeGroupService(db)
    knowledge_group_service.update(group_id, current_user.id, knowledge_group_in)


@router.put(
    "/group/order/{group_id}", response_model=None, status_code=status.HTTP_200_OK
)
async def update_knowledge_group_order(
    group_id: str,
    order_index: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """更新知识库分组排序"""
    knowledge_group_service = KnowledgeGroupService(db)
    knowledge_group_service.change_order_index(group_id, current_user.id, order_index)


@router.delete("/group/{group_id}", response_model=None, status_code=status.HTTP_200_OK)
async def delete_knowledge_group(
    group_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """删除知识库分组"""
    knowledge_group_service = KnowledgeGroupService(db)
    knowledge_group_service.delete(group_id, current_user.id)


@router.get("/group/list", response_model=List[KnowledgeGroupResponse])
async def get_knowledge_group_list(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> List[KnowledgeGroupResponse]:
    """获取知识库分组列表"""
    knowledge_group_service = KnowledgeGroupService(db)
    return knowledge_group_service.get_list_by_user_id(current_user.id)


@router.get("/group/list-detail", response_model=List[KnowledgeGroupResponse])
async def get_knowledge_group_list_detail(
    keyword: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[KnowledgeGroupResponse]:
    """获取带知识库的分组列表"""
    knowledge_group_service = KnowledgeGroupService(db)
    return knowledge_group_service.get_list_with_knowledge(current_user.id, keyword)


@router.put(
    "/group/relation/{knowledge_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
)
async def move_knowledge_group_relation(
    knowledge_id: str,
    move_in: KnowledgeGroupRelationMoveBody,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """移动/排序分组内知识库"""
    relation_service = KnowledgeGroupRelationService(db)
    relation_service.move_relation(current_user.id, knowledge_id, move_in)


@router.get("/{identifier}/document/tree", response_model=List[DocumentNodeResponse])
async def get_document_tree(
    knowledge: Knowledge = Depends(get_knowledge_or_403),
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
) -> List[DocumentNodeResponse]:
    """获取知识库的文档树"""
    document_tree_service = DocumentNodeService(db)
    document_tree = document_tree_service.get_document_tree_nodes(knowledge.id)
    print("取到了文档树", document_tree)
    return document_tree


@router.delete("/{identifier}", response_model=None, status_code=status.HTTP_200_OK)
async def delete_knowledge(
    knowledge: Knowledge = Depends(
        VertifyKnowledgePermission(KnowledgeAbility.DELETE_BOOK)
    ),
    db: Session = Depends(get_db),
) -> bool:
    """删除知识库(软删除)"""
    knowledge_service = KnowledgeService(db)
    return knowledge_service.soft_delete(knowledge.id)


@router.post(
    "/common-pin/create",
    response_model=KnowledgeCommonPinResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_knowledge_common_pin(
    knowledge_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> KnowledgeCommonPinResponse:
    """创建一条常用知识库记录"""
    knowledge_common_pin_service = KnowledgeCommonPinService(db)
    return knowledge_common_pin_service.create(knowledge_id, current_user.id)


@router.put(
    "/common-pin/update/{knowledge_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
)
async def update_knowledge_common_pin(
    knowledge_id: str,
    order_index: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """更新常用知识库记录的排序索引"""
    knowledge_common_pin_service = KnowledgeCommonPinService(db)
    return knowledge_common_pin_service.change_order_index(
        knowledge_id, current_user.id, order_index
    )


@router.get("/common-pin/list", response_model=List[KnowledgeCommonPinResponse])
async def get_knowledge_common_pin_list(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> List[KnowledgeCommonPinResponse]:
    """获取用户常用知识库记录列表"""
    knowledge_common_pin_service = KnowledgeCommonPinService(db)
    return knowledge_common_pin_service.get_list_by_user_id(current_user.id)


@router.delete(
    "/common-pin/{knowledge_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
)
async def delete_knowledge_common_pin(
    knowledge_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """取消常用知识库"""
    knowledge_common_pin_service = KnowledgeCommonPinService(db)
    deleted = knowledge_common_pin_service.delete_by_knowledge_id_and_user_id(
        knowledge_id, current_user.id
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="常用记录不存在"
        )


@router.delete("/{knowledge_id}/leave", response_model=None)
async def leave_knowledge(
    knowledge_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """退出知识库"""
    collaborator_service = CollaboratorService(db)
    collaborator_service.delete_collaborator_by_resource(
        current_user.id, CollaborateResourceType.KNOWLEDGE, knowledge_id
    )
