from app.models.space import Space
from fastapi import HTTPException, status
from app.schemas.space import SpaceCreate, SpaceUpdate
from sqlalchemy.orm import Session
from app.services.base_service import BaseService
from app.models.space_member import SpaceMember
from app.services.space_member_service import SpaceMemberService
from app.schemas.space_member import SpaceMemberCreate
from app.common.enums import SpaceMemberRole, SpaceType
import secrets
import string


class SpaceService(BaseService):
    """空间服务"""

    def __init__(self, db: Session):
        super().__init__(db, Space)

    def get_my_space(self, user_id: int):
        return (
            self.get_active_query()
            .filter(Space.owner_id == user_id, Space.type == SpaceType.PERSONAL)
            .first()
        )

    def _generate_public_area_slug(self, space_domain: str) -> str:
        suffix = "".join(
            secrets.choice(string.ascii_lowercase + string.digits) for _ in range(6)
        )
        return f"org-wiki-{space_domain}-{suffix}"

    def check_domain_avaliable(self, domin: str) -> bool:
        return self.get_active_query().filter(Space.domain == domin).first() is None

    def create_space(self, *, space_create: SpaceCreate, owner_id: int):
        if not self.check_domain_avaliable(space_create.domain):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="空间域名已被使用"
            )
        public_area_slug = self._generate_public_area_slug(space_create.domain)

        space_row = Space(
            **space_create.model_dump(),
            description=space_create.description or "",
            public_area_slug=public_area_slug,
            owner_id=owner_id,
            type=SpaceType.ORGANIZATION,
        )
        self.db.add(space_row)
        self.db.flush()
        # 追加默认成员
        space_member_service = SpaceMemberService(self.db)
        space_member_service.add_member(
            SpaceMemberCreate(
                space_id=space_row.id,
                user_id=space_row.owner_id,
                role=SpaceMemberRole.OWNER,
            ),
            commit=False,
        )
        self.db.commit()
        self.db.refresh(space_row)
        return space_row

    def create_default_space(self, *, owner_id: int, name: str, contact_email: str):
        space_row = Space(
            name=name,
            description="默认空间",
            contact_email=contact_email,
            type=SpaceType.PERSONAL,
            owner_id=owner_id,
        )
        self.db.add(space_row)
        self.db.flush()
        # 追加默认成员
        space_member_service = SpaceMemberService(self.db)
        space_member_service.add_member(
            SpaceMemberCreate(
                space_id=space_row.id,
                user_id=space_row.owner_id,
                role=SpaceMemberRole.OWNER,
            ),
            commit=False,
        )
        return space_row

    def list_spaces_by_user_id(self, user_id: int):
        """查找我加入的空间列表"""
        return (
            self.get_active_query()
            .join(SpaceMember, SpaceMember.space_id == Space.id)
            .filter(
                SpaceMember.user_id == user_id,
                SpaceMember.deleted_at.is_(None),
                Space.type == SpaceType.ORGANIZATION,
            )
            .all()
        )

    def update_space(self, space_update: SpaceUpdate):
        self.db.add(space_update)
        self.db.flush()
        self.db.commit()
        self.db.refresh(space_update)
        return space_update

    def delete_space(self, space_id: str) -> bool:
        space = self.get_active_query().filter(Space.id == space_id).first()
        if space is None:
            return False
        space.soft_delete()
        self.db.commit()
        return True
