from app.models.space import Space
from app.schemas.space import SpaceCreate, SpaceUpdate
from sqlalchemy.orm import Session
from app.services.base_service import BaseService
from typing import Optional
from app.services.space_member_service import SpaceMemberService
from app.schemas.space_member import SpaceMemberCreate
from app.common.enums import SpaceMemberRole


class SpaceService(BaseService):
    """空间服务"""

    def __init__(self, db: Session):
        super().__init__(db, Space)

    def get_space_by_user_id(self, user_id: int):
        return self.get_active_query().filter(Space.owner_id == user_id).first()

    def get_space_by_domin(self, domin: str):
        return self.get_active_query().filter(Space.domain == domin).first()

    def create_space(self, space_create: SpaceCreate):
        space_row = Space(**space_create.model_dump())
        self.db.add(space_row)
        self.db.flush()
        self.db.commit()
        self.db.refresh(space_row)
        return space_row

    def create_default_space(self, space_create: SpaceCreate):
        space_row = Space(**space_create.model_dump())
        self.db.add(space_row)
        self.db.flush()
        # 追加默认成员
        space_member_service = SpaceMemberService(self.db)
        space_member_service.add_member(SpaceMemberCreate(
            space_id=space_row.id,
            user_id=space_row.owner_id,
            role=SpaceMemberRole.OWNER,
        ))
        self.db.refresh(space_row)
        return space_row

    def update_space(self, space_update: SpaceUpdate):
        self.db.add(space_update)
        self.db.flush()
        self.db.commit()
        self.db.refresh(space_update)
        return space_update

    def delete_space(self, space_id: str):
        self.db.query(Space).filter(Space.id == space_id).update(
            {"deleted_at": func.now()}
        )
        self.db.commit()
        return True

    def check_domin_available(self, domin: str) -> bool:
        return self.get_active_query().filter(Space.domain == domin).first() is None
