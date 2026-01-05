from typing import Optional, List
from fastapi import HTTPException, status
from app.schemas.knowledge_collaborator import (
    KnowledgeCollaboratorValidInfo,
    KnowledgeCollaboratorValidParams,
)
from sqlalchemy.orm import Session, joinedload
from app.models.knowledge import Knowledge
from app.models.knowledge_collaborator import KnowledgeCollaborator
from app.schemas.knowledge_collaborator import (
    KnowledgeCollaboratorBase,
    KnowledgeCollaboratorResponse,
    KnowledgeCollaboratorCreate,
    KnowledgeCollaboratorUpdateInfo,
    KnowledgeCollaboratorAudit,
)
from app.common.enums import (
    KnowledgeCollaboratorSource,
    KnowledgeCollaboratorStatus,
    KnowledgeCollaboratorRole,
)


class KnowledgeCollaboratorService:
    """协作者服务"""

    def __init__(self, db: Session):
        self.db = db

    def get_collaborator_valid_info(
        self, collaborator_in: KnowledgeCollaboratorValidParams
    ) -> Optional[KnowledgeCollaboratorValidInfo]:
        """获取协作者校验信息"""

        has_joined_collaborator = (
            self.db.query(KnowledgeCollaborator)
            .filter(
                KnowledgeCollaborator.user_id == collaborator_in.user_id,
                KnowledgeCollaborator.knowledge_id == collaborator_in.knowledge_id,
            )
            .first()
        )
        if has_joined_collaborator is not None:
            return KnowledgeCollaboratorValidInfo(status=has_joined_collaborator.status)

        return None

    def join_default_collaborator(
        self, collaborator_in: KnowledgeCollaboratorCreate, use_by_router: bool = False
    ) -> KnowledgeCollaboratorResponse:
        """加入创建者作为默认协作者"""
        collaborator = KnowledgeCollaborator(
            user_id=collaborator_in.user_id,
            knowledge_id=collaborator_in.knowledge_id,
            status=KnowledgeCollaboratorStatus.ACCEPTED.value,
            source=KnowledgeCollaboratorSource.CREATOR.value,
            role=KnowledgeCollaboratorRole.ADMIN.value,
        )
        self.db.add(collaborator)
        self.db.flush()
        if use_by_router:
            self.db.commit()
        self.db.refresh(collaborator)
        return collaborator

    def join_collaborator(
        self, collaborator_in: KnowledgeCollaboratorBase
    ) -> KnowledgeCollaboratorResponse:
        """加入协作者"""
        collaborator = KnowledgeCollaborator(
            user_id=collaborator_in.user_id,
            knowledge_id=collaborator_in.knowledge_id,
            status=collaborator_in.status.value,
            source=collaborator_in.source.value,
            role=collaborator_in.role.value,
        )
        self.db.add(collaborator)
        self.db.commit()
        self.db.refresh(collaborator)
        # TODO: 发送站内信通知
        return collaborator

    def get_collaborators(
        self, knowledge_id: str
    ) -> List[KnowledgeCollaboratorResponse]:
        """获取协作者列表"""
        collaborators = (
            self.db.query(KnowledgeCollaborator)
            .filter(KnowledgeCollaborator.knowledge_id == knowledge_id)
            .options(joinedload(KnowledgeCollaborator.user))
            .all()
        )
        return collaborators

    def delete_collaborator(self, collaborator_id: str) -> None:
        """删除协作者"""
        collaborator = self.db.query(KnowledgeCollaborator).filter(KnowledgeCollaborator.id == collaborator_id).first()
        if collaborator is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="协作者不存在")
        self.db.delete(collaborator)
        self.db.commit()
        return None

    def update_collaborator_info(self, collaborator_id: str, collaborator_info: KnowledgeCollaboratorUpdateInfo) -> KnowledgeCollaboratorResponse:
        """更新协作者信息"""
        collaborator = self.db.query(KnowledgeCollaborator).filter(KnowledgeCollaborator.id == collaborator_id).first()
        if collaborator is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="协作者不存在")
        update_data = collaborator_info.model_dump(exclude_unset=True, exclude={"id"})
        # 遍历更新数据，如果字段有值则更新（添加了枚举值判断）
        for field_name, field_value in update_data.items():
            if field_value is not None:
                setattr(collaborator, field_name, field_value.value if hasattr(field_value, 'value') else field_value)
        
        self.db.commit()
        self.db.refresh(collaborator)
        return collaborator

    def audit_collaborator(self, collaborator_id: str, audit_in: KnowledgeCollaboratorAudit) -> Optional[KnowledgeCollaboratorResponse]:
        """审核知识库协作者"""
        collaborator = self.db.query(KnowledgeCollaborator).filter(KnowledgeCollaborator.id == collaborator_id).first()
        if collaborator is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="协作者不存在")
        if audit_in.audit_status == 'agree':
            collaborator.status = KnowledgeCollaboratorStatus.ACCEPTED.value
        else:
            self.db.delete(collaborator)
        self.db.commit()
        self.db.refresh(collaborator)
        return collaborator if audit_in.audit_status == 'agree' else None

    def get_user_role_in_knowledge(self, user_id: str, knowledge_id: str) -> Optional[KnowledgeCollaboratorRole]:
        """获取用户在知识库中的角色"""
        collaborator = self.db.query(KnowledgeCollaborator).filter(KnowledgeCollaborator.user_id == user_id, KnowledgeCollaborator.knowledge_id == knowledge_id).first()
        if collaborator:
            return collaborator.role
        # 如果协作者不存在，则判断是否为知识库创建者
        knowledge = self.db.query(Knowledge).filter(Knowledge.id == knowledge_id).first()
        if knowledge and knowledge.user_id == user_id:
            return KnowledgeCollaboratorRole.ADMIN.value

        return None