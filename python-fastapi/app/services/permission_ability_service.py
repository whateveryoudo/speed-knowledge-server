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
            KnowledgeAbility.COLLECT_BOOK: True,
            KnowledgeAbility.CREATE_BOOK: True,
            KnowledgeAbility.CREATE_BOOK_COLLABORATOR: True,
            KnowledgeAbility.EXPORT_BOOK: True,
            KnowledgeAbility.DELETE_BOOK: True,
            KnowledgeAbility.READ_BOOK: True,
            KnowledgeAbility.MODIFY_BOOK_SETTING: True,
            KnowledgeAbility.SHARE_BOOK: True,
            KnowledgeAbility.MODIFY_BOOK_PERMISSION: True,
        },
        ResourceRole.EDIT: {
            KnowledgeAbility.COLLECT_BOOK: True,
            KnowledgeAbility.CREATE_BOOK: False,
            KnowledgeAbility.CREATE_BOOK_COLLABORATOR: False,
            KnowledgeAbility.EXPORT_BOOK: True,
            KnowledgeAbility.DELETE_BOOK: False,
            KnowledgeAbility.READ_BOOK: True,
            KnowledgeAbility.MODIFY_BOOK_SETTING: False,
            KnowledgeAbility.SHARE_BOOK: True,
            KnowledgeAbility.MODIFY_BOOK_PERMISSION: False,
        },
        ResourceRole.READ: {
            KnowledgeAbility.COLLECT_BOOK: True,
            KnowledgeAbility.CREATE_BOOK: False,
            KnowledgeAbility.CREATE_BOOK_COLLABORATOR: False,
            KnowledgeAbility.EXPORT_BOOK: False,
            KnowledgeAbility.DELETE_BOOK: False,
            KnowledgeAbility.READ_BOOK: True,
            KnowledgeAbility.MODIFY_BOOK_SETTING: False,
            KnowledgeAbility.SHARE_BOOK: False,
            KnowledgeAbility.MODIFY_BOOK_PERMISSION: False,
        },
    }

    # 角色权限能力映射(这里是单个文档的能力)
    __default_document_abilities_dict = {
        ResourceRole.ADMIN: {
            DocumentAbility.DOC_CTEATE: True,
            DocumentAbility.DOC_READ: True,
            DocumentAbility.DOC_EDIT: True,
            DocumentAbility.DOC_DELETE: True,
            DocumentAbility.DOC_JOIN: True,
            DocumentAbility.DOC_SHARE: True,
            DocumentAbility.DOC_COMMENT: True,
            DocumentAbility.DOC_EXPORT: True,
        },
        ResourceRole.EDIT: {
            DocumentAbility.DOC_CTEATE: False,
            DocumentAbility.DOC_READ: True,
            DocumentAbility.DOC_EDIT: True,
            DocumentAbility.DOC_DELETE: False,
            DocumentAbility.DOC_JOIN: False,
            DocumentAbility.DOC_SHARE: True,
            DocumentAbility.DOC_COMMENT: False,
            DocumentAbility.DOC_EXPORT: True,
        },
        ResourceRole.READ: {
            DocumentAbility.DOC_CTEATE: False,
            DocumentAbility.DOC_READ: True,
            DocumentAbility.DOC_EDIT: False,
            DocumentAbility.DOC_DELETE: False,
            DocumentAbility.DOC_JOIN: False,
            DocumentAbility.DOC_SHARE: False,
            DocumentAbility.DOC_COMMENT: False,
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
            **cls.__default_document_abilities_dict[ResourceRole.READ],
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
            # 知识库需要合并知识库和文档的权限能力（注意：知识库的只读和文档只读没区别，但是知识库的编辑其实就是文档的admin权限）
            permission_abilities = {
                **self.__default_knowledge_abilities_dict[role_key],
                # 这里作下区分，其实知识库编辑可以理解为有文档的最高权限了
                **self.__default_document_abilities_dict[
                    (role_key if role_key == ResourceRole.READ else ResourceRole.ADMIN)
                ],
            }

        elif scope_type == PermissionScopeType.DOCUMENT:
            permission_abilities = self.__default_document_abilities_dict[role_key]
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
