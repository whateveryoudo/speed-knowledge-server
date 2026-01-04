from typing import Optional, List

from app.schemas.knowledge_collaborator import (
    KnowledgeCollaboratorValidInfo,
    KnowledgeCollaboratorValidParams,
)
from sqlalchemy.orm import Session, joinedload
from app.models.knowledge_collaborator import KnowledgeCollaborator
from app.schemas.knowledge_collaborator import (
    KnowledgeCollaboratorBase,
    KnowledgeCollaboratorResponse,
    KnowledgeCollaboratorCreate,
)
from app.common.enums import (
    KnowledgeCollaboratorSource,
    KnowledgeCollaboratorStatus,
    KnowledgeCollaboratorRole,
)


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

    def join_default_collaborator(
        self, collaborator_in: KnowledgeCollaboratorCreate, use_by_router: bool = False
    ) -> KnowledgeCollaboratorResponse:
        """加入创建者作为默认协作者"""
        collaborator = KnowledgeCollaborator(
            user_id=collaborator_in.user_id,
            knowledge_id=collaborator_in.knowledge_id,
            status=KnowledgeCollaboratorStatus.ACCEPTED.value,
            source=KnowledgeCollaboratorSource.CREATOR.value,
            role=KnowledgeCollaboratorRole.ADMIN.value,
        )
        self.db.add(collaborator)
        self.db.flush()
        if use_by_router:
            self.db.commit()
        self.db.refresh(collaborator)
        return collaborator

    def join_collaborator(
        self, collaborator_in: KnowledgeCollaboratorBase
    ) -> KnowledgeCollaboratorResponse:
        """加入协作者"""
        collaborator = KnowledgeCollaborator(
            user_id=collaborator_in.user_id,
            knowledge_id=collaborator_in.knowledge_id,
            status=collaborator_in.status.value,
            source=collaborator_in.source.value,
            role=collaborator_in.role.value,
        )
        self.db.add(collaborator)
        self.db.commit()
        self.db.refresh(collaborator)
        return collaborator

    def get_collaborators(
        self, knowledge_id: str
    ) -> List[KnowledgeCollaboratorResponse]:
        """获取协作者列表"""
        collaborators = (
            self.db.query(KnowledgeCollaborator)
            .filter(KnowledgeCollaborator.knowledge_id == knowledge_id)
            .options(joinedload(KnowledgeCollaborator.user))
            .all()
        )
        return collaborators
