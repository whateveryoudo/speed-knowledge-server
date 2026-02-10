from typing import Optional, List, Union
from fastapi import HTTPException, status
from app.schemas.collaborator import (
    CollaboratorValidInfo,
    CollaboratorValidParams,
    QueryPermissionGroupParams,
)
from sqlalchemy.orm import Session, joinedload
from app.models.knowledge import Knowledge
from app.models.document import Document
from app.models.collaborator import Collaborator
from app.models.permission_group import PermissionGroup
from app.schemas.collaborator import (
    CollaboratorResponse,
    CollaboratorCreate,
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

    def get_resource_by_slug(
        self, resource_type: CollaborateResourceType, resource_identifier: str
    ) -> Optional[Union[Knowledge, Document]]:
        """获取资源(解决传入短链获取对应id的场景)"""
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
        return resource

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

    def __get_permission_group_by_resource(
        self, collaborator_in: CollaboratorCreate
    ) -> PermissionGroup:
        """通过类型和id查找对应的权限组(已废弃)"""
        permission_group = (
            self.db.query(PermissionGroup)
            .filter(
                PermissionGroup.target_type == collaborator_in.target_type,
                (
                    PermissionGroup.target_id == collaborator_in.knowledge_id
                    if collaborator_in.target_type == CollaborateResourceType.KNOWLEDGE
                    else PermissionGroup.target_id == collaborator_in.document_id
                ),
            )
            .first()
        )
        if permission_group is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="权限组不存在"
            )
        return permission_group

    def join_default_collaborator(
        self, collaborator_in: CollaboratorCreate, use_by_router: bool = False
    ) -> Collaborator:
        """加入创建者作为默认协作者"""
        # permission_group = self.__get_permission_group_by_resource(collaborator_in)
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
        # permission_group = self.__get_permission_group_by_resource(collaborator_in)
        # collaborator_in.permission_group_id = permission_group.id
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

        resource = self.get_resource_by_slug(resource_type, resource_identifier)
        # 定义排序权重(正在审核1，创建者2,其余按照倒序排列)
        sort_order = case(
            (Collaborator.status == CollaboratorStatus.PENDING.value, 1),
            (Collaborator.role == CollaboratorRole.ADMIN.value, 2),
            else_=3,
        )
        if resource_type == CollaborateResourceType.KNOWLEDGE:
            # 知识库协作者查询
            sorted_collaborators = (
                self.db.query(Collaborator)
                .filter(
                    Collaborator.knowledge_id == resource.id,
                    Collaborator.target_type == CollaborateResourceType.KNOWLEDGE,
                )
                .options(joinedload(Collaborator.user))
                .order_by(
                    sort_order, Collaborator.created_at.desc()
                )  # 先按权重排序，再按创建时间排序
                .all()
            )
        else:
            # 文档协作者查询(这里需要同步查询对应知识库的协作者)
            document_collaborators = (
                self.db.query(Collaborator)
                .filter(Collaborator.document_id == resource.id)
                .options(joinedload(Collaborator.user))
                .order_by(
                    sort_order, Collaborator.created_at.desc()
                )  # 先按权重排序，再按创建时间排序
                .all()
            )
            # 查询知识库当前文档所属知识库的协作者
            knowledge_collaborators = (
                self.db.query(Collaborator)
                .filter(
                    Collaborator.knowledge_id == resource.knowledge_id,
                    Collaborator.status == CollaboratorStatus.ACCEPTED.value,
                    Collaborator.target_type
                    == CollaborateResourceType.KNOWLEDGE.value,  # 只查询知识库协作者
                )  # 只显示已接受的)
                .options(joinedload(Collaborator.user))
                .order_by(
                    sort_order, Collaborator.created_at.desc()
                )  # 先按权重排序，再按创建时间排序
                .all()
            )
            all_collaborators = list(document_collaborators) + list(
                knowledge_collaborators
            )
            # 排序：进行中>文档>知识库>
            sorted_collaborators = sorted(
                all_collaborators,
                key=lambda x: (
                    0 if x.status == CollaboratorStatus.ACCEPTED.value else 1,
                    1 if x.document_id == resource.id else 2,
                    x.created_at,
                ),
            )

        return sorted_collaborators

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

    def get_to_audit_count(
        self, resource_type: CollaborateResourceType, resource_identifier: str
    ) -> int:
        """获取待审批数量(这里传入的是协作者短链)"""
        resource = self.get_resource_by_slug(resource_type, resource_identifier)
        return (
            self.db.query(Collaborator)
            .filter(
                Collaborator.target_type == resource_type,
                (
                    Collaborator.knowledge_id == resource.id
                    if resource_type == CollaborateResourceType.KNOWLEDGE
                    else (
                        Collaborator.document_id == resource.id
                        if resource_type == CollaborateResourceType.KNOWLEDGE
                        else Collaborator.document_id == resource.id
                    )
                ),
                Collaborator.status == CollaboratorStatus.PENDING.value,
            )
            .count()
        )

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

    def get_collaborator_by_resource(
        self, query_params: QueryPermissionGroupParams
    ) -> Optional[Collaborator]:
        """通过资源类型和资源id,用户id查找对应的协作者记录"""
        print(query_params.target_id)
        target_row = (
            self.db.query(Collaborator)
            .filter(
                (
                    Collaborator.knowledge_id == query_params.target_id
                    if query_params.target_type.value
                    == CollaborateResourceType.KNOWLEDGE
                    else Collaborator.document_id == query_params.target_id
                ),
                Collaborator.user_id == query_params.user_id,
                Collaborator.status == CollaboratorStatus.ACCEPTED.value,
            )
            .first()
        )
        if target_row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="协作信息不存在"
            )
        return target_row
