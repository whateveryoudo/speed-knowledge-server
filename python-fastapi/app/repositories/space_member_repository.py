from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.repositories import SoftDeleteRepository
from app.models.space_member import SpaceMember
from app.models.space_department import SpaceDepartmentMember
from app.common.enums import SpaceMemberRole
from app.models.user import User
from sqlalchemy.orm import joinedload, Query


class SpaceMemberRepository(SoftDeleteRepository[SpaceMember]):
    def __init__(self, db: Session):
        super().__init__(db, SpaceMember)

    def get_active_by_space_and_user(
        self, *, space_id: str, user_id: int
    ) -> SpaceMember | None:
        return (
            self.active_query()
            .filter(SpaceMember.space_id == space_id, SpaceMember.user_id == user_id)
            .first()
        )

    def get_active_by_id(self, *, member_id: str) -> SpaceMember | None:
        return self.active_query().filter(SpaceMember.id == member_id).first()

    def get_any_by_space_and_user(
        self, *, space_id: str, user_id: int
    ) -> SpaceMember | None:
        return (
            self.all_query()
            .filter(SpaceMember.space_id == space_id, SpaceMember.user_id == user_id)
            .first()
        )

    def build_members_query(
        self,
        *,
        space_id: str,
        tab: str,
        department_ids: list[str] | None = None,
        keyword: str | None = None,
    ) -> Query:
        if tab == "resigned":
            query = self.deleted_query().filter(SpaceMember.space_id == space_id)
        else:
            query = self.active_query().filter(SpaceMember.space_id == space_id)
            if tab == "external":
                query = query.filter(SpaceMember.role == SpaceMemberRole.EXTERNAL)
            else:
                query = query.filter(SpaceMember.role != SpaceMemberRole.EXTERNAL)

        if department_ids and tab != "resigned":
            query = (
                query.join(
                    SpaceDepartmentMember,
                    SpaceDepartmentMember.space_member_id == SpaceMember.id,
                )
                .filter(SpaceDepartmentMember.department_id.in_(department_ids))
                .distinct()
            )

        query = query.join(User, User.id == SpaceMember.user_id).options(
            joinedload(SpaceMember.user)
        )
        if keyword:
            kw = f"%{keyword.strip()}%"
            query = query.filter(
                or_(
                    User.username.like(kw), User.nickname.like(kw), User.email.like(kw)
                )
            )

        return query
