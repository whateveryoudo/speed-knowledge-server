"""权限能力聚合服务"""

from tokenize import group
from typing import Optional, Dict, Union
from sqlalchemy.orm import Session
from app.models.document import Document
from app.common.enums import CollaboratorRole, collaborator_role_name
from app.services.collaborator_service import CollaboratorService
from app.services.document_service import DocumentService
from app.schemas.collaborator import QueryPermissionGroupParams
from app.services.permission_ability_service import PermissionAbilityService
from app.common.enums import CollaborateResourceType, KnowledgeAbility, DocumentAbility

# from app.services.document_collaborator_service import DocumentCollaboratorService


class PermissionService:

    DEFAULT_ABILITY_NAME_DICT = {
        KnowledgeAbility.CREATE_BOOK: "创建知识库",
        KnowledgeAbility.CREATE_BOOK_COLLABORATOR: "创建知识库协作者",
        KnowledgeAbility.EXPORT_BOOK: "导出知识库",
        KnowledgeAbility.READ_BOOK: "访问知识库",
        KnowledgeAbility.DELETE_BOOK: "删除知识库",
        KnowledgeAbility.MODIFY_BOOK_SETTING: "修改知识库设置",
        KnowledgeAbility.SHARE_BOOK: "分享知识库",
        KnowledgeAbility.MODIFY_BOOK_PERMISSION: "修改知识库权限",
        DocumentAbility.DOC_CTEATE: "创建文档",
        DocumentAbility.DOC_READ: "访问文档",
        DocumentAbility.DOC_EDIT: "编辑文档",
        DocumentAbility.DOC_DELETE: "删除文档",
        DocumentAbility.DOC_JOIN: "加入文档",
        DocumentAbility.DOC_SHARE: "分享文档",
        DocumentAbility.DOC_COMMENT: "评论文档",
    }

    def __init__(self, db: Session):
        self.db = db
        self.collaborator_service = CollaboratorService(db)
        self.document_service = DocumentService(db)
        self.permission_ability_service = PermissionAbilityService(db)
        # self.document_collaborator_service = DocumentCollaboratorService(db)

    def get_user_role_in_knowledge(
        self, user_id: int, knowledge_id: str
    ) -> Optional[CollaboratorRole]:
        """获取用户在知识库中的角色"""
        return self.collaborator_service.get_user_role_in_knowledge(
            user_id, knowledge_id
        )

    def can_manage_knowledge(self, user_id: int, knowledge_id: str) -> bool:
        role = self.get_user_role_in_knowledge(user_id, knowledge_id)
        return role in [CollaboratorRole.ADMIN]

    def can_edit_knowledge(self, user_id: int, knowledge_id: str) -> bool:
        role = self.get_user_role_in_knowledge(user_id, knowledge_id)
        return role in [
            CollaboratorRole.ADMIN,
            CollaboratorRole.EDITOR,
        ]

    def can_read_knowledge(
        self, user_id: int, knowledge_id: str, is_public: bool
    ) -> bool:
        role = self.get_user_role_in_knowledge(user_id, knowledge_id)
        return is_public or role is not None

    def can_edit_document(self, user_id: int, document: Document) -> bool:
        # 如果是创建者
        if document.user_id == user_id:
            return True
        # 知识库角色
        knowledge_role = self.get_user_role_in_knowledge(user_id, document.knowledge_id)

        if knowledge_role and knowledge_role in [
            CollaboratorRole.ADMIN,
            CollaboratorRole.EDIT,
        ]:
            return True
        # TODO:当前文档的协同角色
        return False

    def can_read_document(self, user_id: int, document: Document) -> bool:
        # 如果是创建者
        if document.user_id == user_id:
            return True
        # 知识库角色
        knowledge_role = self.get_user_role_in_knowledge(user_id, document.knowledge_id)

        if knowledge_role is not None:
            return True
        # TODO:当前文档的协同角色
        return False

    def get_permission_ability_by_resource(
        self, user_id: int, target_type: CollaborateResourceType, target_id: str
    ) -> Optional[Dict[Union[KnowledgeAbility, DocumentAbility], bool]]:
        """通过资源类型和资源id,用户id查找对应的权限能力"""
        target_collaborator = self.collaborator_service.get_collaborator_by_resource(
            QueryPermissionGroupParams(
                user_id=user_id, target_type=target_type, target_id=target_id
            )
        )
        if target_collaborator is None:
            return None
        # 拿到关联的权限组多条记录，筛选出当前role对应的权限组信息
        groups = target_collaborator.permission_groups or []
        group = next((g for g in groups if g.role == target_collaborator.role), None)
        if group is None:
            return None
        abilities = self.permission_ability_service.get_ability_by_permission_group_id(
            group.id
        )
        return {ability.ability_key: ability.enable for ability in abilities}
