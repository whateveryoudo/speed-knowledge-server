"""知识库端点"""

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm.session import Session
from typing import List, Optional
from app.schemas.knowledge import KnowledgeCreate, KnowledgeResponse, KnowledgeIndexPageResponse, KnowledgeFullResponse
from app.core.deps import get_db, get_current_user, get_knowledge_or_403
from app.models.user import User
from app.models.knowledge import Knowledge
from app.services.knowledge_service import KnowledgeService
from app.services.knowledge_group_service import KnowledgeGroupService
from app.services.knowledge_invitation_service import KnowledgeInvitationService
from app.services.knowledge_collaborator_service import KnowledgeCollaboratorService
from app.services.document_node_service import DocumentNodeService
from app.schemas.document_node import DocumentNodeResponse
from app.services.knowledge_daily_stats_service import KnowledgeDailyStatsService
from app.schemas.knowledge_daily_stats import KnowledgeDailyStatsResponse
from app.services.collect_service import CollectService
from app.schemas.response import BaseResponse
from app.schemas.knowledge_collaborator import (
    KnowledgeCollaboratorBase,
    KnowledgeCollaboratorRequest,
    KnowledgeCollaboratorResponse,
    KnowledgeCollaboratorValidParams,
    KnowledgeCollaboratorCreate,
    KnowledgeCollaboratorUpdate,
    KnowledgeCollaboratorAudit

)
from app.common.enums import (
    KnowledgeInvitationStatus,
    KnowledgeCollaboratorStatus,
    KnowledgeCollaboratorSource,
    CollectResourceType,
)
from app.schemas.knowledge_group import (
    KnowledgeGroupUpdate,
    KnowledgeGroupResponse,
    KnowledgeGroupCreate,
)
from app.schemas.knowledge_invitation import (
    KnowledgeInvitationResponse,
    KnowledgeInvitationBase,
)

from app.schemas.knowledge_invitation import KnowledgeInvitationValidResponse

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
    return created_knowledge.id


@router.get("/list", response_model=List[KnowledgeResponse])
async def get_knowledge_list(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> List[Knowledge]:
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
        knowledge_daily_stats = knowledge_daily_stats_service.get_daily_stats_by_knowledge_id(knowledge.id)
        knowledge_daily_stats_schema = (KnowledgeDailyStatsResponse.model_validate(knowledge_daily_stats) if knowledge_daily_stats else None)
        collected_record = collect_service.check_is_collected(current_user.id, knowledge.id, CollectResourceType.KNOWLEDGE)
        # 合并一些属性
        return KnowledgeIndexPageResponse(**knowledge_index_page_schema.model_dump(),
            word_count=knowledge_daily_stats_schema.word_count if knowledge_daily_stats_schema else 0,
            has_collected=collected_record is not None,
        )
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="知识库不存在")

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
    return document_tree


@router.get(
    "/{knowledge_identifier}/invitation/token",
    response_model=KnowledgeInvitationResponse,
)
async def get_invitation_token(
    knowledge_identifier: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> KnowledgeInvitationResponse:
    """获取知识库邀请链接token信息"""
    invitation_token_service = KnowledgeInvitationService(db)
    invitation_token_info = invitation_token_service.get_invitation_token(
        knowledge_identifier
    )
    return invitation_token_info


@router.put(
    "/invitation/token/{invitation_id}", response_model=KnowledgeInvitationResponse
)
async def update_invitation_token(
    invitation_id: str,
    invitation_token_update: KnowledgeInvitationBase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> KnowledgeInvitationResponse:
    """更新知识库邀请链接token信息(权限或是否需要审核)"""
    invitation_token_service = KnowledgeInvitationService(db)
    invitation_token_info = invitation_token_service.update_invitation_token(
        invitation_id,
        invitation_token_update
    )
    return invitation_token_info


@router.post(
    "/{knowledge_id}/invitation/token/reset/{invitation_id}",
    response_model=KnowledgeInvitationResponse,
)
async def reset_invitation_token(
    invitation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> KnowledgeInvitationResponse:
    """重置知识库邀请链接token信息"""
    invitation_token_service = KnowledgeInvitationService(db)
    invitation_token_info = invitation_token_service.reset_invitation_token(
        invitation_id
    )
    return invitation_token_info


@router.get("/invitation/valid", response_model=KnowledgeInvitationValidResponse)
async def get_invitation_valid_info(
    invitation_token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> KnowledgeInvitationValidResponse:
    """获取邀请链接校验信息"""
    invitation_service = KnowledgeInvitationService(db)
    collaborator_service = KnowledgeCollaboratorService(db)
    invitation_valid_info = invitation_service.get_invitation_valid_info(
        invitation_token
    )
    if (
        invitation_valid_info is None
        or invitation_valid_info.status == KnowledgeInvitationStatus.REVOKED
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="邀请链接已失效"
        )
    collaborator_valid_info = collaborator_service.get_collaborator_valid_info(
        KnowledgeCollaboratorValidParams(
            knowledge_id=invitation_valid_info.knowledge_id,
            user_id=current_user.id,
        )
    )
    return KnowledgeInvitationValidResponse(
        invitation=invitation_valid_info, collaborator=collaborator_valid_info
    )


@router.get("/{knowledge_id}/collaborator/list", response_model=List[KnowledgeCollaboratorResponse])
async def get_collaborator_list(
    knowledge_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[KnowledgeCollaboratorResponse]:
    """获取知识库协作者列表"""
    collaborator_service = KnowledgeCollaboratorService(db)
    collaborators = collaborator_service.get_collaborators(knowledge_id)
    return collaborators


@router.post(
    "/collaborator/default/create", response_model=KnowledgeCollaboratorResponse
)
async def create_default_collaborator(
    default_collaborator_in: KnowledgeCollaboratorCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> KnowledgeCollaboratorResponse:
    """创建默认协作者(用于测试，之前没加)"""
    collaborator_service = KnowledgeCollaboratorService(db)
    return collaborator_service.join_default_collaborator(
        KnowledgeCollaboratorCreate(
            user_id=current_user.id,
            knowledge_id=default_collaborator_in.knowledge_id,
        ),
        use_by_router=True,
    )


@router.post("/invitation/apply", response_model=KnowledgeCollaboratorResponse)
async def apply_invitation(
    invitation_info: KnowledgeCollaboratorRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> KnowledgeCollaboratorResponse:
    """点击申请加入知识库"""
    # 先校验是否合法
    invitation_service = KnowledgeInvitationService(db)
    collaborator_service = KnowledgeCollaboratorService(db)
    invitation_valid_info = invitation_service.get_invitation_by_token(
        invitation_info.invitation_token
    )
    if (
        invitation_valid_info is None
        or invitation_valid_info.status == KnowledgeInvitationStatus.REVOKED
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="邀请链接已失效"
        )
    collaborator_valid_info = collaborator_service.get_collaborator_valid_info(
        KnowledgeCollaboratorValidParams(
            knowledge_id=invitation_valid_info.knowledge_id,
            user_id=current_user.id,
        )
    )
    print(invitation_valid_info)
    if (
        collaborator_valid_info
        
    ):
        if collaborator_valid_info.status == KnowledgeCollaboratorStatus.ACCEPTED.value:
            return BaseResponse.success_reponse(data=collaborator_valid_info, message="您已加入该知识库")
        elif collaborator_valid_info.status == KnowledgeCollaboratorStatus.PENDING.value:
            return BaseResponse.success_reponse(data=collaborator_valid_info, message="等待管理员审核")

    # 根据邀请链接的配置初始化协作者状态
    collaborator_status = (
        KnowledgeCollaboratorStatus.PENDING.value
        if invitation_valid_info.need_approval == 1
        else KnowledgeCollaboratorStatus.ACCEPTED.value
    )
    temp_collaborator_info = KnowledgeCollaboratorBase(
        user_id=current_user.id,
        knowledge_id=invitation_valid_info.knowledge_id,
        status=collaborator_status,
        source=KnowledgeCollaboratorSource.INVITATION.value,
        role=invitation_valid_info.role,
    )
    return collaborator_service.join_collaborator(temp_collaborator_info)

@router.delete("/collaborator/{collaborator_id}", response_model=None, status_code=status.HTTP_200_OK)
async def delete_collaborator(
    collaborator_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """删除知识库协作者"""
    collaborator_service = KnowledgeCollaboratorService(db)
    collaborator_service.delete_collaborator(collaborator_id)

@router.put("/collaborator/{collaborator_id}", response_model=KnowledgeCollaboratorResponse)
async def update_collaborator_info(
    collaborator_id: str,
    collaborator_info: KnowledgeCollaboratorUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> KnowledgeCollaboratorResponse:
    """更新知识库协作者信息"""
    collaborator_service = KnowledgeCollaboratorService(db)
    return collaborator_service.update_collaborator_info(collaborator_id, collaborator_info)

@router.post("/collaborator/{collaborator_id}/audit", response_model=KnowledgeCollaboratorResponse)
async def audit_collaborator(
    collaborator_id: str,
    audit_in: KnowledgeCollaboratorAudit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Optional[KnowledgeCollaboratorResponse]:
    """审核知识库协作者"""
    collaborator_service = KnowledgeCollaboratorService(db)
    return collaborator_service.audit_collaborator(collaborator_id, audit_in)