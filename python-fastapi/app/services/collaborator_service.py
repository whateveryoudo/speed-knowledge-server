from typing import Optional, List
from fastapi import HTTPException, status
from app.schemas.collaborator import (
    CollaboratorValidInfo,
    CollaboratorValidParams,
)
from sqlalchemy.orm import Session, joinedload
from app.models.knowledge import Knowledge
from app.models.document import Document
from app.models.collaborator import Collaborator
from app.schemas.collaborator import (
    CollaboratorBase,
    CollaboratorResponse,
    CollaboratorCreate,
    CollaboratorUpdate,
    CollaboratorAudit,
)
from app.common.enums import (
    CollaboratorSource,
    CollaboratorStatus,
    CollaboratorRole,
    CollaborateResourceType,
)


class CollaboratorService:
    """协作者服务"""

    def __init__(self, db: Session):
        self.db = db

    def get_collaborator_valid_info(
        self, collaborator_in: CollaboratorValidParams
    ) -> Optional[CollaboratorValidInfo]:
        """获取协作者校验信息"""

        has_joined_collaborator = (
            self.db.query(Collaborator)
            .filter(
                Collaborator.user_id == collaborator_in.user_id,
                (
                    Collaborator.knowledge_id == collaborator_in.knowledge_id
                    if collaborator_in.resource_type
                    == CollaborateResourceType.KNOWLEDGE
                    else Collaborator.document_id == collaborator_in.document_id
                ),
            )
            .first()
        )
        if has_joined_collaborator is not None:
            return CollaboratorValidInfo(status=has_joined_collaborator.status)

        return None

    def join_default_collaborator(
        self, collaborator_in: CollaboratorCreate, use_by_router: bool = False
    ) -> CollaboratorResponse:
        """加入创建者作为默认协作者"""
        if collaborator_in.target_type == CollaborateResourceType.KNOWLEDGE:
            collaborator = Collaborator(
                user_id=collaborator_in.user_id,
                knowledge_id=collaborator_in.knowledge_id,
                status=CollaboratorStatus.ACCEPTED.value,
                source=CollaboratorSource.CREATOR.value,
                role=CollaboratorRole.ADMIN.value,
                target_type=CollaborateResourceType.KNOWLEDGE.value,
            )
        else:
            collaborator = Collaborator(
                user_id=collaborator_in.user_id,
                document_id=collaborator_in.document_id,
                status=CollaboratorStatus.ACCEPTED.value,
                source=CollaboratorSource.CREATOR.value,
                role=CollaboratorRole.ADMIN.value,
                target_type=CollaborateResourceType.DOCUMENT.value,
            )
        self.db.add(collaborator)
        self.db.flush()
        if use_by_router:
            self.db.commit()
        self.db.refresh(collaborator)
        return collaborator

    def join_collaborator(self, collaborator_in: Collaborator) -> CollaboratorResponse:
        """加入协作者"""
        self.db.add(collaborator_in)
        self.db.flush()
        self.db.commit()
        self.db.refresh(collaborator_in)
        # TODO: 发送站内信通知
        return collaborator_in

    def get_collaborators(
        self, resource_type: CollaborateResourceType, resource_identifier: str
    ) -> List[CollaboratorResponse]:
        """获取协作者列表(这里需要根据短链先获取对应的id)"""
        from sqlalchemy import case

        resource_model = (
            Knowledge
            if resource_type == CollaborateResourceType.KNOWLEDGE
            else Document
        )
        resource = (
            self.db.query(resource_model)
            .filter(resource_model.slug == resource_identifier)
            .first()
        )
        if resource is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="资源不存在"
            )
        # 定义排序权重(正在审核1，创建者2,其余按照倒序排列)
        sort_order = case(
            (Collaborator.status == CollaboratorStatus.PENDING.value, 1),
            (Collaborator.role == CollaboratorRole.ADMIN.value, 2),
            else_=3,
        )
        collaborators = (
            self.db.query(Collaborator)
            .filter(
                Collaborator.knowledge_id == resource.id
                if resource_type == CollaborateResourceType.KNOWLEDGE
                else Collaborator.document_id == resource.id
            )
            .options(joinedload(Collaborator.user))
            .order_by(
                sort_order, Collaborator.created_at.desc()
            )  # 先按权重排序，再按创建时间排序
            .all()
        )
        return collaborators

    def delete_collaborator(self, collaborator_id: str) -> None:
        """删除协作者"""
        collaborator = (
            self.db.query(Collaborator)
            .filter(Collaborator.id == collaborator_id)
            .first()
        )
        if collaborator is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="协作者不存在"
            )
        self.db.delete(collaborator)
        self.db.commit()
        return None

    def update_collaborator_info(
        self, collaborator_id: str, collaborator_info: CollaboratorUpdateInfo
    ) -> CollaboratorResponse:
        """更新协作者信息"""
        collaborator = (
            self.db.query(Collaborator)
            .filter(Collaborator.id == collaborator_id)
            .first()
        )
        if collaborator is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="协作者不存在"
            )
        update_data = collaborator_info.model_dump(exclude_unset=True, exclude={"id"})
        # 遍历更新数据，如果字段有值则更新（添加了枚举值判断）
        for field_name, field_value in update_data.items():
            if field_value is not None:
                setattr(
                    collaborator,
                    field_name,
                    field_value.value if hasattr(field_value, "value") else field_value,
                )

        self.db.commit()
        self.db.refresh(collaborator)
        return collaborator

    def audit_collaborator(
        self, collaborator_id: str, audit_in: CollaboratorAudit
    ) -> Optional[CollaboratorResponse]:
        """审核知识库协作者"""
        collaborator = (
            self.db.query(Collaborator)
            .filter(Collaborator.id == collaborator_id)
            .first()
        )
        if collaborator is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="协作者不存在"
            )
        if audit_in.audit_status == "agree":
            collaborator.status = CollaboratorStatus.ACCEPTED.value
        else:
            self.db.delete(collaborator)
        self.db.commit()
        self.db.refresh(collaborator)
        return collaborator if audit_in.audit_status == "agree" else None

    def get_user_role_in_knowledge(
        self, user_id: str, knowledge_id: str
    ) -> Optional[CollaboratorRole]:
        """获取用户在知识库中的角色(需要是已经加入的)"""
        collaborator = (
            self.db.query(Collaborator)
            .filter(
                Collaborator.user_id == user_id,
                Collaborator.knowledge_id == knowledge_id,
                Collaborator.status == CollaboratorStatus.ACCEPTED.value,
            )
            .first()
        )
        if collaborator:
            return collaborator.role
        # 如果协作者不存在，则判断是否为知识库创建者
        knowledge = (
            self.db.query(Knowledge).filter(Knowledge.id == knowledge_id).first()
        )
        if knowledge and knowledge.user_id == user_id:
            return CollaboratorRole.ADMIN.value

        return None
