"""权限判断服务（知识库/文档）"""

from typing import Optional
from sqlalchemy.orm import Session
from app.models.document import Document
from app.common.enums import KnowledgeCollaboratorRole
from app.services.knowledge_collaborator_service import KnowledgeCollaboratorService
from app.services.document_service import DocumentService

# from app.services.document_collaborator_service import DocumentCollaboratorService


class PermissionService:
    def __init__(self, db: Session):
        self.db = db
        self.knowledge_collaborator_service = KnowledgeCollaboratorService(db)
        self.document_service = DocumentService(db)
        # self.document_collaborator_service = DocumentCollaboratorService(db)

    def get_user_role_in_knowledge(
        self, user_id: int, knowledge_id: str
    ) -> Optional[KnowledgeCollaboratorRole]:
        """获取用户在知识库中的角色"""
        return self.knowledge_collaborator_service.get_user_role_in_knowledge(
            user_id, knowledge_id
        )

    def can_manage_knowledge(self, user_id: int, knowledge_id: str) -> bool:
        role = self.get_user_role_in_knowledge(user_id, knowledge_id)
        return role in [KnowledgeCollaboratorRole.ADMIN]

    def can_edit_knowledge(self, user_id: int, knowledge_id: str) -> bool:
        role = self.get_user_role_in_knowledge(user_id, knowledge_id)
        return role in [
            KnowledgeCollaboratorRole.ADMIN,
            KnowledgeCollaboratorRole.EDITOR,
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

        if knowledge_role and knowledge_role in [KnowledgeCollaboratorRole.ADMIN, KnowledgeCollaboratorRole.EDIT]:
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
        
