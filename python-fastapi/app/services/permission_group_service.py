from typing import Optional
from sqlalchemy.orm import Session
from app.common.enums import CollaboratorRole, collaborator_role_name
from app.schemas.permission_group import (
    PermissionGroupCreate,
    PermissionGroupUpdate,
    PermissionGroupResponse,
)
from app.models.permission_group import PermissionGroup
from app.services.permission_ability_service import PermissionAbilityService
from app.schemas.permission_ability import PermissionAbilityCreateByRole


class PermissionGroupService:
    """权限组服务"""

    def __init__(self, db: Session):
        self.db = db

    def create_permission_group(
        self, permission_group_in: PermissionGroupCreate
    ) -> PermissionGroup:
        """创建权限组"""
        permission_group = PermissionGroup(
            **permission_group_in.model_dump()
        )
        print(permission_group)

        self.db.add(permission_group)
        self.db.flush()
        # 增加权限组的时候需要同步增加对应的权限能力
        permission_ability_service = PermissionAbilityService(self.db)
        permission_ability_service.create_permission_ability_by_role(
            PermissionAbilityCreateByRole(
                permission_group_id=permission_group.id,
                role=permission_group_in.role,
                target_type=permission_group_in.target_type,
            )
        )
        self.db.commit()
        return permission_group

    def get_permission_group_by_id(self, permission_group_id: str):
        """根据ID获取权限组"""
        return (
            self.db.query(PermissionGroup)
            .filter(PermissionGroup.id == permission_group_id)
            .first()
        )
