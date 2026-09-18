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
    DocumentVisibility,
)

from app.models.permission_ability import PermissionAbility
from app.models.knowledge import Knowledge
from app.services.resource_grant_service import ResourceGrantService


AbilityKey: TypeAlias = KnowledgeAbility | DocumentAbility
AbilityMap: TypeAlias = dict[AbilityKey, bool]


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
        KnowledgeAbility.CREATE_DOCUMENT: "创建文档",
        DocumentAbility.DOC_READ: "访问文档",
        DocumentAbility.DOC_EDIT: "编辑文档",
        DocumentAbility.DOC_DELETE: "删除文档",
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
        self,
        *,
        user_id: int,
        knowledge: Knowledge,
        include_visibility_scope: bool = True,
    ) -> AbilityMap:
        """获取用户在知识库中的有效能力"""
        role = self.resource_grant_service.resolve_granted_knowledge_role(
            user_id=user_id,
            knowledge=knowledge,
            include_visibility_scope=include_visibility_scope,
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

        include_parent_visibility_scope = (
            document.visibility == DocumentVisibility.INHERIT.value
        )

        knowledge_abilities = self.get_effective_knowledge_abilities(
            user_id=user_id,
            knowledge=document.knowledge,
            include_visibility_scope=include_parent_visibility_scope,
        )
        document_abilities: AbilityMap = {}
        document_role = self.resource_grant_service.resolve_granted_document_role(
            user_id=user_id, document=document
        )

        if document_role is not None:
            document_group = self.permission_group_repository.get_by_scope_role(
                scope_type=PermissionScopeType.DOCUMENT,
                scope_id=document.id,
                role_key=document_role.value,
            )
            if document_group is not None:
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
            self.assert_document_ability(user_id, target_id, DocumentAbility.DOC_SHARE)
            return
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

    def assert_resource_readable(
        self, *, user_id: int, resource_type: ResourceType, identifier: str
    ) -> None:
        """资源是否可读"""
        if resource_type == ResourceType.KNOWLEDGE:
            self.assert_knowledge_readable(user_id, identifier)
        elif resource_type == ResourceType.DOCUMENT:
            self.assert_document_readable(user_id, identifier)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="不支持的资源类型"
            )

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
        """判断用户是否可读取文档"""
        if document.visibility == DocumentVisibility.PUBLIC.value:
            return True
        if user_id is None:
            # 只有inherit且知识库公开时才运行游客访问
            return (
                document.visibility == DocumentVisibility.INHERIT.value
                and document.knowledge.visibility == KnowledgeVisibility.PUBLIC.value
            )
        abilities = self.get_effective_document_abilities(
            user_id=user_id, document=document
        )
        return bool(abilities.get(DocumentAbility.DOC_READ, False))

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

    def list_readable_documents_by_ids(
        self, *, user_id: int | None, document_ids: list[str]
    ) -> list[Document]:
        """根据ID获取父链有效且当前用户可读的文档"""
        unique_ids = list(dict.fromkeys(document_ids))
        if not unique_ids:
            return []
        active_documents = self.document_repository.list_active_by_ids(unique_ids)
        active_document_by_id = {document.id: document for document in active_documents}

        # 按照传入id返回
        return [
            active_document_by_id[document_id]
            for document_id in unique_ids
            if document_id in active_document_by_id
            and self.can_read_document(user_id, active_document_by_id[document_id])
        ]

    def resolve_multiple_document_readabilities(
        self, *, user_id: int | None, documents: list[Document]
    ) -> dict[str, bool]:
        """批量解析文档是否可读（排除祖先链无效的文档）"""
        document_ids = list(dict.fromkeys([document.id for document in documents]))
        if not document_ids:
            return {}
        readable_document_ids = {
            document.id
            for document in self.list_readable_documents_by_ids(
                user_id=user_id, document_ids=document_ids
            )
        }

        return {
            document_id: document_id in readable_document_ids
            for document_id in document_ids
        }

    def filter_readable_documents(
        self, *, user_id: int | None, documents: list[Document]
    ) -> list[Document]:
        """过滤出用户可读的文档"""
        readability_by_id = self.resolve_multiple_document_readabilities(
            user_id=user_id, documents=documents
        )
        return [
            document
            for document in documents
            if readability_by_id.get(document.id, False)
        ]

    def filter_document_readable_user_ids(
        self, *, document: Document, user_ids: list[int]
    ) -> list[int]:
        """过滤出对同一温度最终具有读取能力的用户ID"""
        unique_user_ids = list(dict.fromkeys(user_ids))
        # TODO:后续替换成实际批量查询
        if not unique_user_ids:
            return []
        return [
            user_id
            for user_id in unique_user_ids
            if self.can_read_document(user_id, document)
        ]

    def list_readable_knowledges_by_ids(
        self, *, user_id: int | None, knowledge_ids: list[str]
    ) -> list[Knowledge]:
        """根据ID获取父链有效且当前用户可读的知识库"""
        unique_ids = list(dict.fromkeys(knowledge_ids))
        if not unique_ids:
            return []
        active_knowledges = self.knowledge_repository.list_active_by_ids(unique_ids)
        active_knowledge_by_id = {
            knowledge.id: knowledge for knowledge in active_knowledges
        }
        return [
            active_knowledge_by_id[knowledge_id]
            for knowledge_id in unique_ids
            if knowledge_id in active_knowledge_by_id
            and self.can_read_knowledge(user_id, active_knowledge_by_id[knowledge_id])
        ]

    def resolve_multiple_knowledge_readabilities(
        self, *, user_id: int | None, knowledges: list[Knowledge]
    ) -> dict[str, bool]:
        """批量解析知识库是否可读(排除祖先链无效的知识库)，目前先试用循环单条，后续替换为批量获取和能力查询"""
        knowledge_ids = list(dict.fromkeys([knowledge.id for knowledge in knowledges]))
        if not knowledge_ids:
            return {}
        readable_knowledge_ids = {
            knowledge.id
            for knowledge in self.list_readable_knowledges_by_ids(
                user_id=user_id, knowledge_ids=knowledge_ids
            )
        }
        return {
            knowledge_id: knowledge_id in readable_knowledge_ids
            for knowledge_id in knowledge_ids
        }

    def filter_readable_knowledges(
        self, *, user_id: int | None, knowledges: list[Knowledge]
    ) -> list[Knowledge]:
        """过滤出用户可读的知识库"""
        readability_by_id = self.resolve_multiple_knowledge_readabilities(
            user_id=user_id, knowledges=knowledges
        )
        return [
            knowledge
            for knowledge in knowledges
            if readability_by_id.get(knowledge.id, False)
        ]
