"""权限能力聚合服务"""
from typing import TypeAlias
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.document import Document
from app.services.permission_ability_service import PermissionAbilityService

from app.repositories.knowledge_repository import KnowledgeRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.permission_group_repository import PermissionGroupRepository
from app.common.enums import (
    ResourceType,
    KnowledgeAbility,
    DocumentAbility,
    KnowledgeVisibility,
    PermissionScopeType,
)

from app.models.permission_ability import PermissionAbility
from app.models.knowledge import Knowledge
from app.services.resource_grant_service import ResourceGrantService


AbilityKey: TypeAlias = KnowledgeAbility | DocumentAbility
AbilityMap: TypeAlias = dict[AbilityKey, bool]


class PermissionService:

    DEFAULT_ABILITY_NAME_DICT = {
        KnowledgeAbility.CREATE_BOOK: "创建知识库",
        KnowledgeAbility.COLLECT_BOOK: "收藏知识库",
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
        DocumentAbility.DOC_EXPORT: "导出文档",
    }

    def __init__(self, db: Session):
        self.db = db

        self.knowledge_repository = KnowledgeRepository(db)
        self.document_repository = DocumentRepository(db)
        self.permission_group_repository = PermissionGroupRepository(db)

        self.resource_grant_service = ResourceGrantService(db)

    def get_effective_knowledge_abilities(
        self, *, user_id: int, knowledge: Knowledge
    ) -> AbilityMap:
        """获取用户在知识库中的有效能力"""
        role = self.resource_grant_service.resolve_granted_knowledge_role(
            user_id=user_id, knowledge=knowledge
        )
        if role is None:
            return {}
        group = self.permission_group_repository.get_by_scope_role(
            scope_type=PermissionScopeType.KNOWLEDGE,
            scope_id=knowledge.id,
            role_key=role.value,
        )
        if group is None:
            return {}
        return self._build_ability_dict(group.abilities)

    def get_effective_document_abilities(
        self, *, user_id: int, document: Document
    ) -> AbilityMap:
        """获取用户在文档中的有效能力"""
        knowledge_abilities = self.get_effective_knowledge_abilities(
            user_id=user_id, knowledge=document.knowledge
        )

        document_role = self.resource_grant_service.resolve_granted_document_role(
            user_id=user_id, document=document
        )
        if document_role is None:
            return knowledge_abilities
        document_group = self.permission_group_repository.get_by_scope_role(
            scope_type=PermissionScopeType.DOCUMENT,
            scope_id=document.id,
            role_key=document_role.value,
        )
        if document_group is None:
            return knowledge_abilities
        document_abilities = self._build_ability_dict(document_group.abilities)
        # 合并知识库和文档的能力
        return self._merge_ability_maps(knowledge_abilities, document_abilities)

    def _ability_denied_message(self, ability: AbilityKey) -> str:
        return f"你无权{self.DEFAULT_ABILITY_NAME_DICT[ability]}"

    def assert_knowledge_ability(
        self,
        user_id: int,
        identifier: str,
        ability: AbilityKey,
    ) -> Knowledge:
        """封装一层知识库是否拥有某项能力（用于deps和其他一些场景）"""

        target_knowledge = self.knowledge_repository.get_active_by_id_or_slug(
            identifier
        )
        if target_knowledge is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="知识库不存在"
            )
        if not self.has_resource_ability(
            user_id=user_id,
            resource_type=ResourceType.KNOWLEDGE,
            resource_id=target_knowledge.id,
            ability=ability,
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=self._ability_denied_message(ability),
            )
        return target_knowledge

    def assert_document_ability(
        self, user_id: int, identifier: str, ability: DocumentAbility
    ) -> Document:
        """封装一层文档的某项能力（用于deps和其他一些场景）"""

        target_document = self.document_repository.get_active_by_id_or_slug(identifier)
        if not target_document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在"
            )
        if not self.has_resource_ability(
            user_id=user_id,
            resource_type=ResourceType.DOCUMENT,
            resource_id=target_document.id,
            ability=ability,
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=self._ability_denied_message(ability),
            )
        return target_document

    def assert_can_manage_access_setting(
        self, user_id: int, target_type: ResourceType, target_id: str
    ) -> None:
        """访问高级配置的密码权限"""
        if target_type == ResourceType.KNOWLEDGE:
            self.assert_knowledge_ability(
                user_id, target_id, KnowledgeAbility.MODIFY_BOOK_PERMISSION
            )
            return
        if target_type == ResourceType.DOCUMENT:
            abilities = self.get_effective_abilities(
                user_id=user_id,
                resource_type=target_type,
                resource_id=target_id,
            )
            can_share = bool(abilities.get(DocumentAbility.DOC_SHARE, False))
            can_manage_knowledge = bool(
                abilities.get(KnowledgeAbility.MODIFY_BOOK_PERMISSION, False)
            )
            if can_share and can_manage_knowledge:
                return
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="你无权管理该文档的访问配置",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="不支持的资源类型"
        )

    def assert_knowledge_readable(
        self, user_id: int | None, identifier: str
    ) -> Knowledge:
        """知识库是否可读（含 is_public）"""

        knowledge = self.knowledge_repository.get_active_by_id_or_slug(identifier)
        if knowledge is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="知识库不存在",
            )
        if not self.can_read_knowledge(user_id, knowledge):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="你无权访问此知识库",
            )
        return knowledge

    def assert_document_readable(
        self, user_id: int | None, identifier: str
    ) -> Document:
        """封装一层文档是否可读（用于deps和其他一些场景）"""

        document = self.document_repository.get_active_by_id_or_slug(identifier)
        if document is None:
            raise HTTPException(status_code=404, detail="文档不存在")
        if not self.can_read_document(user_id, document):
            raise HTTPException(status_code=403, detail="你无权访问此文档")
        return document

    def can_read_knowledge(self, user_id: int | None, knowledge: Knowledge) -> bool:
        """知识库是否可读（这里增加了公开知识库访问）"""
        if knowledge.visibility == KnowledgeVisibility.PUBLIC.value:
            return True
        if user_id is None:
            return False
        return self.has_resource_ability(
            user_id=user_id,
            resource_type=ResourceType.KNOWLEDGE,
            resource_id=knowledge.id,
            ability=KnowledgeAbility.READ_BOOK,
        )

    def can_read_document(self, user_id: int | None, document: Document) -> bool:
        if document.is_public:
            return True
        if document.knowledge.visibility == KnowledgeVisibility.PUBLIC.value:
            return True
        if user_id is None:
            return False
        # 如果是创建者
        if document.user_id == user_id:
            return True
        return self.has_resource_ability(
            user_id=user_id,
            resource_type=ResourceType.DOCUMENT,
            resource_id=document.id,
            ability=DocumentAbility.DOC_READ,
        )

    @staticmethod
    def _build_ability_dict(abilities: list[PermissionAbility]) -> AbilityMap:
        """权限能力列表—>能力字典"""
        result: AbilityMap = {}
        for ability in abilities:
            key: AbilityKey | None = ability.ability_key
            try:
                enum_key = KnowledgeAbility(key)
            except ValueError:
                try:
                    enum_key = DocumentAbility(key)
                except ValueError:
                    enum_key = None
            if enum_key is not None:
                result[enum_key] = ability.enabled
        return result

    @staticmethod
    def _merge_ability_maps(*ability_maps: AbilityMap) -> AbilityMap:
        """合并多个能力字典"""
        result: AbilityMap = {}
        for ability_map in ability_maps:
            for key, value in ability_map.items():
                result[key] = result.get(key, False) or value
        return result

    def get_guest_readonly_abilities(self) -> dict:
        """用于获取游客的权限能力(全部只读)"""
        return PermissionAbilityService.get_guest_readonly_abilities()

    def get_multiple_effective_knowledge_abilities(
        self, *, user_id: int, knowledge_ids: list[str]
    ) -> dict[str, AbilityMap]:
        """批量获取用户在知识库的最终能力"""
        unique_ids = list(dict.fromkeys(knowledge_ids))
        result: dict[str, AbilityMap] = {
            knowledge_id: {} for knowledge_id in unique_ids
        }
        if not unique_ids:
            return result
        knowledges = self.knowledge_repository.list_active_by_ids(unique_ids)
        if not knowledges:
            return result
        groups = self.permission_group_repository.list_by_scopes(
            scope_type=PermissionScopeType.KNOWLEDGE,
            scope_ids=[knowledge.id for knowledge in knowledges],
        )
        role_by_knowledge_id = (
            self.resource_grant_service.resolve_multiple_granted_knowledge_roles(
                user_id=user_id, knowledges=knowledges
            )
        )
        groups_by_scope_role = {
            (group.scope_id, group.role_key): group for group in groups
        }

        for knowledge in knowledges:
            role = role_by_knowledge_id.get(knowledge.id)
            if role is None:
                continue
            group = groups_by_scope_role.get((knowledge.id, role.value))
            if group is None:
                continue
            result[knowledge.id] = self._build_ability_dict(group.abilities)
        return result

    def has_resource_ability(
        self,
        *,
        user_id: int,
        resource_type: ResourceType,
        resource_id: str,
        ability: AbilityKey,
    ) -> bool:
        """判断用户是否拥有资源的能力"""
        abilities = self.get_effective_abilities(
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
        )
        return abilities.get(ability, False)

    def get_effective_abilities(
        self, *, user_id: int, resource_type: ResourceType, resource_id: str
    ) -> AbilityMap:
        """通过资源类型和资源id,用户id查找对应的权限能力"""
        if resource_type == ResourceType.KNOWLEDGE:
            knowledge = self.knowledge_repository.get_active_by_id(resource_id)
            if knowledge is None:
                return {}
            return self.get_effective_knowledge_abilities(
                user_id=user_id, knowledge=knowledge
            )
        elif resource_type == ResourceType.DOCUMENT:
            document = self.document_repository.get_active_by_id(resource_id)
            if document is None:
                return {}
            return self.get_effective_document_abilities(
                user_id=user_id, document=document
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="不支持的资源类型",
            )
