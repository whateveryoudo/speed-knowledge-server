from app.models.resource_access_setting import ResourceAccessSetting
from sqlalchemy.orm import Session
from app.schemas.resource_access import (
    ResourceAccessCreate,
    BaseResourceAccess,
    ResourceAccessResponse,
    ResourceAccessUpdate,
)
from app.services.permission_service import PermissionService
from typing import Optional


class ResourceAccessService:
    """资源访问服务"""

    def __init__(self, db: Session):
        self.db = db
        self.permission_service = PermissionService(db)

    def create(
        self, user_id: int, resource_in: ResourceAccessCreate
    ) -> ResourceAccessResponse:
        """创建资源访问"""
        # 权限拦截
        self.permission_service.assert_can_manage_access_setting(
            user_id, resource_in.target_type, resource_in.target_id
        )
        # 判断是否已经新建过(这里不直接用查询方法，否则会重复鉴权)
        row = (
            self.db.query(ResourceAccessSetting)
            .filter(
                ResourceAccessSetting.target_id == resource_in.target_id,
                ResourceAccessSetting.target_type == resource_in.target_type,
            )
            .first()
        )
        if row:
            return row
        resource_access = ResourceAccessSetting(
            target_id=resource_in.target_id,
            target_type=resource_in.target_type,
            password=resource_in.password,
        )
        self.db.add(resource_access)
        self.db.commit()
        self.db.refresh(resource_access)
        return resource_access

    def get(self, id: str) -> ResourceAccessResponse:
        """获取资源访问(这里是id访问)"""
        resource_access = (
            self.db.query(ResourceAccessSetting)
            .filter(ResourceAccessSetting.id == id)
            .first()
        )
        if resource_access:
            return resource_access
        return None

    def get_by_target_id_and_target_type(
        self, user_id: int, resource_in: BaseResourceAccess
    ) -> ResourceAccessSetting:
        """根据目标ID和目标类型获取资源访问"""
        # 权限拦截
        self.permission_service.assert_can_manage_access_setting(
            user_id,
            resource_in.target_type,
            resource_in.target_id,
        )
        return (
            self.db.query(ResourceAccessSetting)
            .filter(
                ResourceAccessSetting.target_id == resource_in.target_id,
                ResourceAccessSetting.target_type == resource_in.target_type,
            )
            .first()
        )

    def update(
        self, user_id: int, id: str, update_in: ResourceAccessUpdate
    ) -> Optional[ResourceAccessResponse]:
        """更新资源访问(id更新属性)"""
        resource_access = self.get(id)
        if not resource_access:
            return None
        # 权限拦截
        self.permission_service.assert_can_manage_access_setting(
            user_id,
            resource_access.target_type,
            resource_access.target_id,
        )
        for key, value in update_in.model_dump().items():
            setattr(resource_access, key, value)
        self.db.commit()
        self.db.refresh(resource_access)
        return resource_access

    def delete(self, user_id: int, id: str) -> bool:
        """删除资源访问(这里通过id进行删除)"""
        row = self.get(id)
        if not row:
            return False
        # 权限拦截
        self.permission_service.assert_can_manage_access_setting(
            user_id,
            row.target_type,
            row.target_id,
        )
        self.db.delete(row)
        self.db.commit()
        return True
