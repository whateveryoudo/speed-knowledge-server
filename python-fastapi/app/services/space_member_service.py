from app.models.space_member import SpaceMember
from app.schemas.space_member import SpaceMemberCreate, SpaceMemberUpdate
from sqlalchemy.orm import Session
from app.services.base_service import BaseService
from app.common.enums import SpaceMemberRole
from typing import Sequence, Optional
from fastapi import HTTPException, status
from app.common.utils import to_enum_value, to_enum_values


class SpaceMemberService(BaseService):
    """空间成员服务"""

    def __init__(self, db: Session):
        super().__init__(db, SpaceMember)

    def get_space_member(self, space_member_id: str):
        return (
            self.db.query(SpaceMember).filter(SpaceMember.id == space_member_id).first()
        )

    def get_member_by_user_id(
        self, *, space_id: str, user_id: int
    ) -> Optional[SpaceMember]:
        return (
            self.db.query(SpaceMember)
            .filter(SpaceMember.space_id == space_id, SpaceMember.user_id == user_id)
            .first()
        )

    def add_member(self, space_member_create: SpaceMemberCreate, commit: bool = True):
        space_member_row = SpaceMember(**space_member_create.model_dump())
        self.db.add(space_member_row)
        self.db.flush()
        if commit:
            self.db.commit()
        self.db.refresh(space_member_row)
        return space_member_row

    def update_space_member(self, space_member_update: SpaceMemberUpdate):
        self.db.add(space_member_update)
        self.db.flush()
        self.db.commit()
        self.db.refresh(space_member_update)
        return space_member_update

    def delete_space_member(self, space_member_id: str):
        self.db.query(SpaceMember).filter(
            SpaceMember.id == space_member_id
        ).first().delete()
        self.db.commit()
        return True

    def ensure_member_role(
        self,
        *,
        space_id: str,
        user_id: int,
        allow_roles: Sequence[SpaceMemberRole] | SpaceMemberRole | None = None,
    ) -> SpaceMember:
        """校验团队成员以及角色权限"""
        member = self.get_member_by_user_id(space_id=space_id, user_id=user_id)
        if member is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="你不是空间成员")
        if allow_roles is not None:
            allowed_set = to_enum_values(allow_roles)
            if to_enum_value(member.role) not in allowed_set:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="你无权执行此操作"
                )
        return member
