from typing import List, Union
from sqlalchemy.orm import Session
from app.models.document import Document
from app.common.enums import (
    ResourceRole,
    KnowledgeAbility,
    DocumentAbility,
    PermissionScopeType,
)
from app.schemas.permission_ability import (
    PermissionAbilityCreateByRole,
)
from app.models.permission_ability import PermissionAbility


class PermissionAbilityService:
    """权限能力服务"""

    # 角色权限能力映射(知识库本身能力)
    __default_knowledge_abilities_dict = {
        ResourceRole.ADMIN: {
            KnowledgeAbility.CREATE_BOOK: True,
            KnowledgeAbility.CREATE_BOOK_COLLABORATOR: True,
            KnowledgeAbility.EXPORT_BOOK: True,
            KnowledgeAbility.DELETE_BOOK: True,
            KnowledgeAbility.READ_BOOK: True,
            KnowledgeAbility.MODIFY_BOOK_SETTING: True,
            KnowledgeAbility.SHARE_BOOK: True,
            KnowledgeAbility.MODIFY_BOOK_PERMISSION: True,
            KnowledgeAbility.CREATE_DOCUMENT: True,
        },
        ResourceRole.EDIT: {
            KnowledgeAbility.CREATE_BOOK: False,
            KnowledgeAbility.CREATE_BOOK_COLLABORATOR: False,
            KnowledgeAbility.EXPORT_BOOK: True,
            KnowledgeAbility.DELETE_BOOK: False,
            KnowledgeAbility.READ_BOOK: True,
            KnowledgeAbility.MODIFY_BOOK_SETTING: False,
            KnowledgeAbility.SHARE_BOOK: True,
            KnowledgeAbility.MODIFY_BOOK_PERMISSION: False,
            KnowledgeAbility.CREATE_DOCUMENT: True,
        },
        ResourceRole.READ: {
            KnowledgeAbility.CREATE_BOOK: False,
            KnowledgeAbility.CREATE_BOOK_COLLABORATOR: False,
            KnowledgeAbility.EXPORT_BOOK: False,
            KnowledgeAbility.DELETE_BOOK: False,
            KnowledgeAbility.READ_BOOK: True,
            KnowledgeAbility.MODIFY_BOOK_SETTING: False,
            KnowledgeAbility.SHARE_BOOK: False,
            KnowledgeAbility.MODIFY_BOOK_PERMISSION: False,
            KnowledgeAbility.CREATE_DOCUMENT: False,
        },
    }
    # 这里拆分成两套矩阵能力
    __knowledge_document_abilities_dict = {
        ResourceRole.ADMIN: {
            DocumentAbility.DOC_READ: True,
            DocumentAbility.DOC_EDIT: True,
            DocumentAbility.DOC_DELETE: True,
            DocumentAbility.DOC_SHARE: True,
            DocumentAbility.DOC_COMMENT: True,
            DocumentAbility.DOC_EXPORT: True,
        },
        ResourceRole.EDIT: {
            DocumentAbility.DOC_READ: True,
            DocumentAbility.DOC_EDIT: True,
            DocumentAbility.DOC_DELETE: False,
            DocumentAbility.DOC_SHARE: True,
            DocumentAbility.DOC_COMMENT: True,
            DocumentAbility.DOC_EXPORT: True,
        },
        ResourceRole.READ: {
            DocumentAbility.DOC_READ: True,
            DocumentAbility.DOC_EDIT: False,
            DocumentAbility.DOC_DELETE: False,
            DocumentAbility.DOC_SHARE: False,
            DocumentAbility.DOC_COMMENT: True,
            DocumentAbility.DOC_EXPORT: False,
        },
    }
    # 单篇文档直接授权能力
    __direct_document_abilities_dict = {
        ResourceRole.EDIT: {
            DocumentAbility.DOC_READ: True,
            DocumentAbility.DOC_EDIT: True,
            DocumentAbility.DOC_DELETE: False,
            DocumentAbility.DOC_SHARE: False,
            DocumentAbility.DOC_COMMENT: True,
            DocumentAbility.DOC_EXPORT: True,
        },
        ResourceRole.READ: {
            DocumentAbility.DOC_READ: True,
            DocumentAbility.DOC_EDIT: False,
            DocumentAbility.DOC_DELETE: False,
            DocumentAbility.DOC_SHARE: False,
            DocumentAbility.DOC_COMMENT: True,
            DocumentAbility.DOC_EXPORT: False,
        },
    }

    def __init__(self, db: Session):
        self.db = db

    @classmethod
    def get_guest_readonly_abilities(cls) -> dict:
        """用于获取游客的权限能力(全部只读)"""
        return {
            **cls.__default_knowledge_abilities_dict[ResourceRole.READ],
            **cls.__knowledge_document_abilities_dict[ResourceRole.READ],
            # 游客不允许评论(这里是匿名游客)
            DocumentAbility.DOC_COMMENT: False,
        }

    def create_permission_abilities_by_role(
        self, permission_ability_in: PermissionAbilityCreateByRole
    ) -> None:
        """创建权限能力(通过角色)"""
        scope_type = permission_ability_in.scope_type
        try:
            role_key = ResourceRole(permission_ability_in.role_key)
        except ValueError as e:
            raise ValueError(
                f"不支持的角色标识: {permission_ability_in.role_key}"
            ) from e
        if scope_type == PermissionScopeType.KNOWLEDGE:
            # 知识库需要合并知识库和文档的权限能力
            permission_abilities = {
                **self.__default_knowledge_abilities_dict[role_key],
                **self.__knowledge_document_abilities_dict[role_key],
            }

        elif scope_type == PermissionScopeType.DOCUMENT:
            if role_key not in (ResourceRole.EDIT, ResourceRole.READ):
                raise ValueError("单篇文档仅支持read/edit角色")
            permission_abilities = self.__direct_document_abilities_dict[role_key]
        else:
            raise ValueError(f"不支持的作用域类型: {scope_type}")
        for ability_key, enabled in permission_abilities.items():
            permission_ability = PermissionAbility(
                permission_group_id=permission_ability_in.permission_group_id,
                ability_key=ability_key.value,
                enabled=enabled,
            )
            self.db.add(permission_ability)
        self.db.flush()

    def add_permission_ability_by_permission_group_id(
        self,
        permission_group_id: str,
        ability_key: Union[KnowledgeAbility, DocumentAbility],
        enabled: bool,
    ) -> None:
        """通过权限组id,添加权限能力"""
        permission_ability = PermissionAbility(
            permission_group_id=permission_group_id,
            ability_key=ability_key.value,
            enabled=enabled,
        )
        self.db.add(permission_ability)
        self.db.flush()

    def get_multiple_abilities_by_permission_group_ids(
        self, permission_group_ids: List[str]
    ) -> List[PermissionAbility]:
        """通过权限组id列表,批量获取权限能力集合"""
        return (
            self.db.query(PermissionAbility)
            .filter(PermissionAbility.permission_group_id.in_(permission_group_ids))
            .all()
        )

    def get_ability_by_permission_group_id(
        self, permission_group_id: str
    ) -> List[PermissionAbility]:
        """通过权限组id获取权限能力集合"""
        return (
            self.db.query(PermissionAbility)
            .filter(PermissionAbility.permission_group_id == permission_group_id)
            .all()
        )
