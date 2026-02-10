"""知识库服务"""

from tokenize import group
from sqlalchemy.orm.session import Session
from app.schemas.knowledge import KnowledgeCreate
from app.models.knowledge import Knowledge
from app.models.collaborator import Collaborator
from sqlalchemy import or_, and_
from app.schemas.collaborator import CollaboratorCreate
from app.services.collaborator_service import CollaboratorService
from app.common.enums import CollaboratorStatus, KnowledgeFromWay
from app.services.permission_group_service import PermissionGroupService
from app.schemas.permission_group import PermissionGroupCreate
from app.models.document import Document
from app.services.permission_service import PermissionService
from app.common.enums import (
    CollaboratorRole,
    CollaborateResourceType,
    collaborator_role_name,
)
from typing import List
import secrets
import string
from datetime import datetime
from app.services.base_service import BaseService
from app.schemas.knowledge import KnowledgeResponse


alphabet = string.ascii_letters + string.digits


class KnowledgeService(BaseService):
    """知识库服务"""

    def to_wrap_knowledge_response(
        self, knowledge: Knowledge, user_id: int
    ) -> KnowledgeResponse:
        """包装知识库响应(追加一些其他参数)"""
        ability = self.permission_service.get_permission_ability_by_resource(
            user_id, CollaborateResourceType.KNOWLEDGE, knowledge.id
        )
        return KnowledgeResponse.model_validate(knowledge).model_copy(
            update={
                "ability": ability,
            }
        )

    def _generate_slug(self) -> str:
        """生成知识库短链"""
        return "".join(secrets.choice(alphabet) for _ in range(6))

    def __init__(self, db: Session) -> None:
        super().__init__(db, Knowledge)
        self.permission_service = PermissionService(db)

    def create(self, knowledge_in: KnowledgeCreate) -> Knowledge:
        """创建知识库"""
        temp_slug = self._generate_slug()
        while self.get_active_query().filter(Knowledge.slug == temp_slug).first():
            temp_slug = self._generate_slug()
        # 默认isPublic为False
        knowledge = Knowledge(
            user_id=knowledge_in.user_id,
            name=knowledge_in.name,
            team_id=knowledge_in.team_id,
            group_id=knowledge_in.group_id,
            icon=knowledge_in.icon,
            slug=temp_slug,
            space_id=knowledge_in.space_id,
            description=knowledge_in.description,
        )
        self.db.add(knowledge)
        self.db.flush()
        # 追加默认协作者
        collaborator_service = CollaboratorService(self.db)
        target_collaborator = collaborator_service.join_default_collaborator(
            CollaboratorCreate(
                user_id=knowledge_in.user_id,
                knowledge_id=knowledge.id,
                target_type=CollaborateResourceType.KNOWLEDGE,
            )
        )
        # 创建默认权限组(追加3个角色权限)
        for role in CollaboratorRole:
            permission_group_service = PermissionGroupService(self.db)
            permission_group_service.create_permission_group(
                # 权限组名称: 知识库名称(知识库短链)-角色名称
                PermissionGroupCreate(
                    name=f"{knowledge.name}({knowledge.slug})-{collaborator_role_name[role.value]}",
                    role=role,
                    collaborator_id=target_collaborator.id,
                    target_type=CollaborateResourceType.KNOWLEDGE,
                    target_id=knowledge.id,
                )
            )

        self.db.commit()
        self.db.refresh(knowledge)
        return knowledge

    def get_by_id_or_slug(self, identifier: str) -> Knowledge:
        """通过知识库id/短链查询知识库(附带文档数量)"""
        knowledge = (
            self.get_active_query()
            .filter(
                or_(Knowledge.id == identifier, Knowledge.slug == identifier),
            )
            .first()
        )
        if knowledge:
            items_count = (
                self.db.query(Document)
                .filter(Document.knowledge_id == knowledge.id)
                .count()
            )
            knowledge.items_count = items_count
        return knowledge

    def get_list_by_user_id(self, user_id: int) -> List[KnowledgeResponse]:
        """通过用户id和团队id查询知识库列表"""
        # 新增逻辑，追加协作者知识库查询
        rows = (
            self.get_active_query()
            .with_entities(Knowledge, Collaborator.id.label("collaborator_id"))
            .outerjoin(
                Collaborator,
                and_(
                    Knowledge.id == Collaborator.knowledge_id,
                    Collaborator.user_id == user_id,
                    Collaborator.status == CollaboratorStatus.ACCEPTED.value,
                    Collaborator.user_id
                    != Knowledge.user_id,  # 排除 协作者是创建者这条记录
                ),
            )
            .filter(
                or_(
                    Knowledge.user_id == user_id,
                    Collaborator.id.isnot(None),
                )
            )
            .distinct()
            .order_by(Knowledge.created_at.desc())
            .all()
        )
        # 结构组装（直接返回pydantic模型）
        result: List[KnowledgeResponse] = []
        for knowledge, collaborator_id in rows:
            item = KnowledgeResponse.model_validate(knowledge, from_attributes=True)
            ability = self.permission_service.get_permission_ability_by_resource(
                user_id, CollaborateResourceType.KNOWLEDGE, knowledge.id
            )
            self.to_wrap_knowledge_response(knowledge, user_id)
            item = item.model_copy(
                update={
                    "ability": ability,
                    "source": (
                        KnowledgeFromWay.OWN
                        if knowledge.user_id == user_id
                        else KnowledgeFromWay.COLLABORATION
                    ),
                    "collaborator_id": collaborator_id,
                }
            )
            result.append(item)
        return result

    def soft_delete(self, knowledge_id: str) -> bool:
        """软删除知识库"""
        knowledge = self.get_active_query().filter(Knowledge.id == knowledge_id).first()
        if knowledge:
            knowledge.deleted_at = datetime.now()
            self.db.commit()
            return True
        return False
