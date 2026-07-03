from fastapi import APIRouter, status, Depends, HTTPException, Query, Path
from app.schemas.resource_access import (
    ResourceAccessCreate,
    BaseResourceAccess,
    ResourceAccessResponse,
    ResourceAccessUpdate,
)
from app.services.resource_access_service import ResourceAccessService
from app.core.deps import get_current_user, get_db
from app.models.user import User
from sqlalchemy.orm.session import Session
from app.common.enums import CollaborateResourceType

router = APIRouter()


@router.post(
    "/", response_model=ResourceAccessResponse, status_code=status.HTTP_201_CREATED
)
async def create_resource_access(
    resource_access_create: ResourceAccessCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResourceAccessResponse:
    """创建资源访问"""
    resource_access_service = ResourceAccessService(db)
    return resource_access_service.create(current_user.id, resource_access_create)


@router.put(
    "/{id}",
    response_model=ResourceAccessResponse,
    status_code=status.HTTP_200_OK,
)
def update_resource_access(
    id: str,
    update_in: ResourceAccessUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResourceAccessResponse:
    """更新资源访问(这里是通过id进行更新)"""
    resource_access_service = ResourceAccessService(db)
    return resource_access_service.update(current_user.id, id, update_in)


@router.delete(
    "/{id}",
    response_model=bool,
    status_code=status.HTTP_200_OK,
)
def delete_resource_access(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> bool:
    """删除资源访问(这里是通过id进行删除)"""
    resource_access_service = ResourceAccessService(db)
    return resource_access_service.delete(current_user.id, id)


@router.get(
    "/get-by-target/{target_type}/{target_id}",
    response_model=ResourceAccessResponse,
    status_code=status.HTTP_200_OK,
)
def get_resource_access(
    target_id: str = Path(..., description="目标id"),
    target_type: CollaborateResourceType = Path(..., description="目标类型"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResourceAccessResponse:
    """获取资源访问(这里是通过类型和目标id)"""
    resource_access_service = ResourceAccessService(db)
    return resource_access_service.get_by_target_id_and_target_type(
        current_user.id,
        BaseResourceAccess(target_id=target_id, target_type=target_type),
    )
