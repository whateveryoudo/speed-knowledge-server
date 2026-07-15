"""权限能力聚合服务"""

from fastapi import HTTPException, status
from typing import Optional, Dict, Union, List
from sqlalchemy.orm import Session
from app.models.document import Document
from app.common.enums import CollaboratorRole, collaborator_role_name
from app.services.collaborator_service import CollaboratorService
from app.services.document_service import DocumentService
from app.schemas.collaborator import QueryPermissionGroupParams
from app.services.permission_ability_service import PermissionAbilityService
from app.common.enums import CollaborateResourceType, KnowledgeAbility, DocumentAbility
from app.services.permission_group_service import PermissionGroupService
from app.models.permission_group import PermissionGroup

# from app.services.document_collaborator_service import DocumentCollaboratorService
from app.models.collaborator import Collaborator
from collections import defaultdict
from app.models.permission_ability import PermissionAbility
from app.models.knowledge import Knowledge


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
        self.permission_group_service = PermissionGroupService(db)
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
            CollaboratorRole.EDIT,
        ]

    def _ability_denied_message(
        self, ability: Union[KnowledgeAbility, DocumentAbility]
    ) -> str:
        return f"你无权{self.DEFAULT_ABILITY_NAME_DICT[ability]}"

    def _get_knowledge_ability_map(
        self, user_id: int, knowledge_id: str
    ) -> Dict[Union[KnowledgeAbility, DocumentAbility], bool]:
        return (
            self.get_permission_ability_by_resource(
                user_id, CollaborateResourceType.KNOWLEDGE, knowledge_id
            )
            or {}
        )

    def _get_merged_document_ability_map(
        self, user_id: int, document: Document
    ) -> Dict[Union[KnowledgeAbility, DocumentAbility], bool]:
        """合并知识库+ 文档自身的 ability"""
        knowledge_abilities = self._get_knowledge_ability_map(
            user_id, document.knowledge_id
        )
        document_abilities = (
            self.get_permission_ability_by_resource(
                user_id, CollaborateResourceType.DOCUMENT, document.id
            )
            or {}
        )
        merged_abilities: Dict[Union[KnowledgeAbility, DocumentAbility], bool] = {}

        for key in set(knowledge_abilities.keys()) | set(document_abilities.keys()):
            merged_abilities[key] = bool(
                knowledge_abilities.get(key, False)
                or document_abilities.get(key, False)
            )
        return merged_abilities

    def assert_knowledge_ability(
        self, user_id: int, identifier: str, ability: Union[KnowledgeAbility, DocumentAbility]
    ) -> Knowledge:
        """封装一层知识库是否拥有某项能力（用于deps和其他一些场景）"""
        from app.services.knowledge_service import KnowledgeService

        knowledge_service = KnowledgeService(self.db)
        target_knowledge = knowledge_service.get_by_id_or_slug(identifier)
        if not target_knowledge:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="知识库不存在"
            )
        abilities = self._get_knowledge_ability_map(user_id, target_knowledge.id)
        if not abilities.get(ability):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=self._ability_denied_message(ability),
            )
        return target_knowledge

    def assert_document_ability(
        self, user_id: int, identifier: str, ability: DocumentAbility
    ) -> Document:
        """封装一层文档的某项能力（用于deps和其他一些场景）"""
        from app.services.document_service import DocumentService

        document_service = DocumentService(self.db)
        target_document = document_service.get_by_id_or_slug(identifier)
        if not target_document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在"
            )
        abilities = self._get_merged_document_ability_map(user_id, target_document)
        if not abilities.get(ability):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=self._ability_denied_message(ability),
            )
        return target_document

    def assert_can_manage_access_setting(
        self, user_id: int, target_type: CollaborateResourceType, target_id: str
    ) -> None:
        """访问高级配置的密码权限"""
        if target_type == CollaborateResourceType.KNOWLEDGE:
            self.assert_knowledge_ability(
                user_id, target_id, KnowledgeAbility.MODIFY_BOOK_PERMISSION
            )
            return
        if target_type == CollaborateResourceType.DOCUMENT:
            document = self.document_service.get_by_id_or_slug(target_id)
            if not document:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在"
                )
            merged = self._get_merged_document_ability_map(user_id, document)
            can_share = bool(merged.get(DocumentAbility.DOC_SHARE, False))
            can_manage_knowledge = bool(
                merged.get(KnowledgeAbility.MODIFY_BOOK_PERMISSION, False)
            )
            if not (can_share or can_manage_knowledge):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=self._ability_denied_message(DocumentAbility.DOC_SHARE),
                )
            return
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="不支持的资源类型"
        )

    def assert_knowledge_readable(self, user_id: int | None, identifier: str) -> Knowledge:
        """知识库是否可读（含 is_public）"""
        from app.services.knowledge_service import KnowledgeService

        knowledge = KnowledgeService(self.db).get_by_id_or_slug(identifier)
        if not knowledge:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="知识库不存在",
            )
        if not self.can_read_knowledge(user_id, knowledge.id, knowledge.is_public):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="你无权访问此知识库",
            )
        return knowledge

    def assert_document_readable(self, user_id: int | None, identifier: str) -> Document:
        """封装一层文档是否可读（用于deps和其他一些场景）"""
        from app.services.document_service import DocumentService

        document_service = DocumentService(self.db)
        document = document_service.get_by_id_or_slug(identifier)
        if not document:
            raise HTTPException(status_code=404, detail="文档不存在")
        if not self.can_read_document(user_id, document, document.is_public):
            raise HTTPException(status_code=403, detail="你无权访问此文档")
        return document

    def can_read_knowledge(
        self, user_id: int | None, knowledge_id: str, is_public: bool
    ) -> bool:
        """知识库是否可读（这里增加了公开知识库访问）"""
        if is_public:
            return True
        if user_id is None:
            return False
        role = self.get_user_role_in_knowledge(user_id, knowledge_id)
        return role is not None

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

    def can_read_document(
        self, user_id: int | None, document: Document, is_public: bool
    ) -> bool:
        knowledge_is_public = (
            document and document.knowledge and document.knowledge.is_public
        )
        if is_public or knowledge_is_public:
            return True
        if user_id is None:
            return False
        # 如果是创建者
        if document.user_id == user_id:
            return True
        # 知识库角色
        knowledge_role = self.get_user_role_in_knowledge(user_id, document.knowledge_id)

        if knowledge_role is not None:
            return True

        doc_collaborator = self.collaborator_service.get_collaborator_by_resource(
            QueryPermissionGroupParams(
                user_id=user_id,
                target_type=CollaborateResourceType.DOCUMENT,
                target_id=document.id,
            )
        )
        if doc_collaborator is not None:
            return True
        return False

    def _build_ability_dict(
        self, abilities: List[PermissionAbility]
    ) -> Dict[Union[KnowledgeAbility, DocumentAbility], bool]:
        result = {}
        for ability in abilities:
            key = ability.ability_key
            try:
                enum_key = KnowledgeAbility(key)
            except ValueError:
                try:
                    enum_key = DocumentAbility(key)
                except ValueError:
                    enum_key = None
            if enum_key is not None:
                result[enum_key] = ability.enable
        return result

    def get_guest_readonly_abilities(self) -> dict:
        """用于获取游客的权限能力(全部只读)"""
        return PermissionAbilityService.get_guest_readonly_abilities()

    def get_multiple_permission_ability_by_resources(
        self, user_id: int, target_type: CollaborateResourceType, target_ids: List[str]
    ) -> Dict[str, Dict[Union[KnowledgeAbility, DocumentAbility], bool]]:
        """多资源批量查询能力，返回资源id与能力字典的映射"""
        if not target_ids:
            return {}
        # 去重
        target_ids = list(dict.fromkeys(target_ids))

        # 批量查询协同者
        collaborators = (
            self.collaborator_service.get_multiple_collaborators_by_resources(
                user_id, target_type, target_ids
            )
        )
        collab_map: dict[str, Collaborator] = {}
        for collaborator in collaborators:
            target_id = (
                collaborator.knowledge_id
                if target_type == CollaborateResourceType.KNOWLEDGE
                else collaborator.document_id
            )
            if target_id:
                collab_map[target_id] = collaborator

        if not collab_map:
            return {target_id: {} for target_id in target_ids}

        # 根据协同记录筛选出对应角色的权限组信息
        groups = (
            self.permission_group_service.get_multiple_permission_groups_by_resources(
                target_type, target_ids
            )
        )

        groups_by_target: dict[str, list[PermissionGroup]] = defaultdict(list)

        for group in groups:
            groups_by_target[group.target_id].append(group)

        # 遍历协同对象，通过target_id,拿到当前匹配的role对应的groupId
        group_id_by_target: dict[str, str] = {}
        for target_id, collab in collab_map.items():
            matched = next(
                (
                    g
                    for g in groups_by_target.get(target_id, [])
                    if g.role == collab.role
                ),
                None,
            )
            if matched:
                group_id_by_target[target_id] = matched.id

        if not group_id_by_target:
            return {target_id: {} for target_id in target_ids}

        # 批量查询权限能力
        abilities = self.permission_ability_service.get_multiple_abilities_by_permission_group_ids(
            list(group_id_by_target.values())
        )

        # 将能力集合进行按group_id分组合并

        ability_by_group: dict[
            str, Dict[Union[KnowledgeAbility, DocumentAbility], bool]
        ] = defaultdict(list)

        for ability in abilities:
            ability_by_group[ability.permission_group_id].append(ability)

        # 遍历资源id,组装最后的结果
        result: dict[str, Optional[dict]] = {}
        for target_id in target_ids:
            group_id = group_id_by_target.get(target_id)
            if not group_id:
                result[target_id] = None
                continue
            result[target_id] = self._build_ability_dict(
                ability_by_group.get(group_id, [])
            )
        return result

    def get_permission_ability_by_resource(
        self, user_id: int, target_type: CollaborateResourceType, target_id: str
    ) -> Optional[Dict[Union[KnowledgeAbility, DocumentAbility], bool]]:
        """通过资源类型和资源id,用户id查找对应的权限能力"""
        print(
            f"get_permission_ability_by_resource: user_id={user_id}, target_type={target_type}, target_id={target_id}"
        )
        target_collaborator = self.collaborator_service.get_collaborator_by_resource(
            QueryPermissionGroupParams(
                user_id=user_id, target_type=target_type, target_id=target_id
            )
        )
        if target_collaborator is None:
            return None
        # 拿到关联的权限组多条记录，筛选出当前role对应的权限组信息
        groups = self.permission_group_service.get_permission_groups_by_resource(
            target_type, target_id
        )
        group = next((g for g in groups if g.role == target_collaborator.role), None)
        if group is None:
            return None
        abilities = self.permission_ability_service.get_ability_by_permission_group_id(
            group.id
        )
        result = {}
        # 对读取的值包一次，转为枚举
        for ability in abilities:
            key = ability.ability_key
            try:
                enum_key = KnowledgeAbility(key)
            except ValueError:
                try:
                    enum_key = DocumentAbility(key)
                except ValueError:
                    enum_key = None
            if enum_key is not None:
                result[enum_key] = ability.enable
        return result
