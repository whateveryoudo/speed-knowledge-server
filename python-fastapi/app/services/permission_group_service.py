from sqlalchemy.orm import Session
from app.common.enums import (
    PermissionScopeType,
)
from app.schemas.permission_group import (
    PermissionGroupCreate,
)
from app.models.permission_group import PermissionGroup
from app.services.permission_ability_service import PermissionAbilityService
from app.schemas.permission_ability import PermissionAbilityCreateByRole
from app.repositories.permission_group_repository import PermissionGroupRepository


class PermissionGroupService:
    """权限组服务"""

    def __init__(self, db: Session):
        self.db = db
        self.permission_group_repository = PermissionGroupRepository(db)
        self.ability_service = PermissionAbilityService(db)

    def create_permission_group(
        self, permission_group_in: PermissionGroupCreate
    ) -> PermissionGroup:
        """创建权限组"""
        permission_group = PermissionGroup(
            name=permission_group_in.name,
            role_key=permission_group_in.role_key,
            scope_type=permission_group_in.scope_type.value,
            scope_id= str(permission_group_in.scope_id),
        )

        self.permission_group_repository.add(permission_group)
        self.permission_group_repository.flush()
        # 增加权限组的时候需要同步增加对应的权限能力
        self.ability_service.create_permission_abilities_by_role(
            PermissionAbilityCreateByRole(
                permission_group_id=permission_group.id,
                role_key=permission_group_in.role_key,
                scope_type=permission_group_in.scope_type,
            )
        )
        return permission_group

    def get_permission_group_by_id(
        self, permission_group_id: str
    ) -> PermissionGroup | None:
        """根据ID获取权限组"""
        return self.permission_group_repository.get_by_id(permission_group_id)

    def delete_permission_group_by_scope(
        self, scope_type: PermissionScopeType, scope_id: str
    ) -> int:
        """根据作用域类型和作用域id删除对应的权限组(这里同走一个事务)"""
        return self.permission_group_repository.delete_by_scope(
            scope_type=scope_type, scope_id=scope_id
        )
