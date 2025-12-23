from typing import Optional

from app.schemas.knowledge_collaborator import (
    KnowledgeCollaboratorValidInfo,
    KnowledgeCollaboratorValidParams,
)
from sqlalchemy.orm import Session
from app.models.knowledge_collaborator import KnowledgeCollaborator
from app.schemas.knowledge_collaborator import (
    KnowledgeCollaboratorCreate,
    KnowledgeCollaboratorResponse,
)
from app.common.enums import KnowledgeCollaboratorStatus


class KnowledgeCollaboratorService:
    """协作者服务"""

    def __init__(self, db: Session):
        self.db = db

    def get_collaborator_valid_info(
        self, collaborator_in: KnowledgeCollaboratorValidParams
    ) -> Optional[KnowledgeCollaboratorValidInfo]:
        """获取协作者校验信息"""

        has_joined_collaborator = (
            self.db.query(KnowledgeCollaborator)
            .filter(
                KnowledgeCollaborator.user_id == collaborator_in.user_id,
                KnowledgeCollaborator.knowledge_id == collaborator_in.knowledge_id,
            )
            .first()
        )
        if has_joined_collaborator is not None:
            return KnowledgeCollaboratorValidInfo(status=has_joined_collaborator.status)

        return None

    def join_collaborator(
        self, collaborator_in: KnowledgeCollaboratorCreate
    ) -> KnowledgeCollaboratorResponse:
        """加入协作者"""
        collaborator = KnowledgeCollaborator(
            user_id=collaborator_in.user_id,
            knowledge_id=collaborator_in.knowledge_id,
            status=collaborator_in.status,
            source=collaborator_in.source,
        )
        self.db.add(collaborator)
        self.db.commit()
        self.db.refresh(collaborator)
        return collaborator
