from fastapi import APIRouter, Depends
from app.schemas.resource_collaboration import (
    ResourceCollaborationItem,
    ResourceCollaborationQuery,
)
from app.services.resource_collaboration_service import ResourceCollaborationService
from app.models.user import User
from app.core.deps import get_current_user, get_db
from sqlalchemy.orm import Session

router = APIRouter()


@router.get(
    "/knowledge/{knowledge_id}/", response_model=list[ResourceCollaborationItem]
)
def list_knowledge_collaborations(
    knowledge_id: str,
    query: ResourceCollaborationQuery = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ResourceCollaborationItem]:
    resource_collaboration_service = ResourceCollaborationService(db)
    return resource_collaboration_service.list_knowledge_collaborations(
        knowledge_id=knowledge_id, operator_id=current_user.id, query=query
    )
