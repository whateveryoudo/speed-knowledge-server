from typing import Optional
from sqlalchemy.orm import Session
from app.models.document import Document
from app.common.enums import (
    CollaboratorRole,
    CollaborateResourceType,
    KnowledgeAbility,
    DocumentAbility,
)
from app.schemas.permission_ability import (
    PermissionAbilityCreateByRole,
)
from app.models.permission_ability import PermissionAbility


class PermissionAbilityService:
    """权限能力服务"""

    # 角色权限能力映射(知识库本身能力)
    __default_knowledge_abilities_dict = {
        CollaboratorRole.ADMIN: {
            KnowledgeAbility.CREATE_BOOK: True,
            KnowledgeAbility.CREATE_BOOK_COLLABORATOR: True,
            KnowledgeAbility.EXPORT_BOOK: True,
            KnowledgeAbility.MODIFY_BOOK_SETTING: True,
            KnowledgeAbility.SHARE_BOOK: True,
            KnowledgeAbility.MODIFY_BOOK_PERMISSION: True,
        },
        CollaboratorRole.EDIT: {
            KnowledgeAbility.CREATE_BOOK: False,
            KnowledgeAbility.CREATE_BOOK_COLLABORATOR: False,
            KnowledgeAbility.EXPORT_BOOK: True,
            KnowledgeAbility.MODIFY_BOOK_SETTING: False,
            KnowledgeAbility.SHARE_BOOK: True,
            KnowledgeAbility.MODIFY_BOOK_PERMISSION: False,
        },
        CollaboratorRole.READ: {
            KnowledgeAbility.CREATE_BOOK: False,
            KnowledgeAbility.CREATE_BOOK_COLLABORATOR: False,
            KnowledgeAbility.EXPORT_BOOK: False,
            KnowledgeAbility.MODIFY_BOOK_SETTING: False,
            KnowledgeAbility.SHARE_BOOK: False,
            KnowledgeAbility.MODIFY_BOOK_PERMISSION: False,
        },
    }

    # 角色权限能力映射
    __default_document_abilities_dict = {
        CollaboratorRole.ADMIN: {
            DocumentAbility.DOC_CTEATE: True,
            DocumentAbility.DOC_READ: True,
            DocumentAbility.DOC_EDIT: True,
            DocumentAbility.DOC_DELETE: True,
            DocumentAbility.DOC_JOIN: True,
            DocumentAbility.DOC_SHARE: True,
            DocumentAbility.DOC_COMMENT: True,
        },
        CollaboratorRole.EDIT: {
            DocumentAbility.DOC_CTEATE: False,
            DocumentAbility.DOC_READ: False,
            DocumentAbility.DOC_EDIT: True,
            DocumentAbility.DOC_DELETE: False,
            DocumentAbility.DOC_JOIN: False,
            DocumentAbility.DOC_SHARE: True,
            DocumentAbility.DOC_COMMENT: False,
        },
        CollaboratorRole.READ: {
            DocumentAbility.DOC_CTEATE: False,
            DocumentAbility.DOC_READ: False,
            DocumentAbility.DOC_EDIT: False,
            DocumentAbility.DOC_DELETE: False,
            DocumentAbility.DOC_JOIN: False,
            DocumentAbility.DOC_SHARE: False,
            DocumentAbility.DOC_COMMENT: False,
        },
    }

    def __init__(self, db: Session):
        self.db = db

    def create_permission_ability_by_role(
        self, permission_ability_in: PermissionAbilityCreateByRole
    ) -> PermissionAbility:
        """创建权限能力(通过角色)"""
        if permission_ability_in.target_type == CollaborateResourceType.KNOWLEDGE:
            # 知识库需要合并知识库和文档的权限能力
            permission_abilities = {
                **self.__default_knowledge_abilities_dict[permission_ability_in.role],
                **self.__default_document_abilities_dict[permission_ability_in.role],
            }
        else:
            permission_abilities = self.__default_document_abilities_dict[
                permission_ability_in.role
            ]
        for ability_key, enable in permission_abilities.items():
            permission_ability = PermissionAbility(
                permission_group_id=permission_ability_in.permission_group_id,
                ability_key=ability_key,
                enable=enable,
            )
            self.db.add(permission_ability)
        self.db.commit()
        return permission_abilities
