from app.models.space_member import SpaceMember
from app.schemas.space_member import SpaceMemberCreate, SpaceMemberUpdate
from sqlalchemy.orm import Session
from app.services.base_service import BaseService


class SpaceMemberService(BaseService):
    """空间成员服务"""

    def __init__(self, db: Session):
        super().__init__(db, SpaceMember)

    def get_space_member(self, space_member_id: str):
        return self.get_active_query().filter(SpaceMember.id == space_member_id).first()

    def add_member(self, space_member_create: SpaceMemberCreate):
        space_member_row = SpaceMember(**space_member_create.model_dump())
        self.db.add(space_member_row)
        self.db.flush()
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
        self.db.query(SpaceMember).filter(SpaceMember.id == space_member_id).update({"deleted_at": func.now()})
        self.db.commit()
        return True
