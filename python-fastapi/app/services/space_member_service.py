from app.common.pagination import paginate_response
from app.schemas.space_member import (
    SpaceMemberItemResponse,
    SpaceMemberExtra,
    SpaceMemberListResponse,
)
from app.models.space_member import SpaceMember
from app.models.space import Space
from sqlalchemy.orm import Session
from app.common.enums import SpaceMemberRole
from app.services.resource_grant_service import ResourceGrantService
from typing import Sequence, Optional
from fastapi import HTTPException, status
from app.repositories.space_department_repository import SpaceDepartmentRepository
from app.repositories.space_member_repository import SpaceMemberRepository
from app.common.utils import to_enum_value, to_enum_values
from app.schemas.space_member import SpaceMemberQuery, SpaceMemberAdd
from app.models.space_department import SpaceDepartment, SpaceDepartmentMember
from app.schemas.user import UserBrief


class SpaceMemberService:
    """空间成员服务"""

    def __init__(self, db: Session):
        self.db = db
        self.resource_grant_service = ResourceGrantService(db)
        self.repo = SpaceMemberRepository(db)
        self.dept_repo = SpaceDepartmentRepository(db)

    def init_space_owner(
        self, *, space_id: str, user_id: int, default_dept_id: str | None = None
    ) -> SpaceMember:
        """初始化空间所有者（创建空间时调用）"""
        if default_dept_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="缺少默认部门"
            )
        member = SpaceMember(
            space_id=space_id,
            user_id=user_id,
            role=SpaceMemberRole.OWNER,
        )
        self.db.add(member)
        self.db.flush()
        if default_dept_id:
            self._sync_member_departments(
                space_member_id=member.id, dept_ids=[default_dept_id]
            )
        return member

    def get_space_member(self, space_member_id: str):
        return (
            self.db.query(SpaceMember).filter(SpaceMember.id == space_member_id).first()
        )

    def get_member_by_user_id(
        self, *, space_id: str, user_id: int
    ) -> Optional[SpaceMember]:
        return self.repo.get_any_by_space_and_user(space_id=space_id, user_id=user_id)

    def _get_deparment_active_member_count(
        self, *, space_id: str, department_id: str | None
    ) -> int:
        """获取部门在职成员数（含子部门，排除已离职和外部人员）"""
        base_query = self.db.query(SpaceMember.id).filter(
            SpaceMember.space_id == space_id,
            SpaceMember.deleted_at.is_(None),
            SpaceMember.role != SpaceMemberRole.EXTERNAL,
        )
        if not department_id:
            return base_query.distinct().count()
        sub_ids = self.dept_repo.get_all_sub_dept_ids(
            space_id=space_id, root_dept_id=department_id
        )
        return (
            base_query.join(
                SpaceDepartmentMember,
                SpaceDepartmentMember.space_member_id == SpaceMember.id,
            )
            .filter(SpaceDepartmentMember.department_id.in_([department_id] + sub_ids))
            .distinct()
            .count()
        )

    def list_members(self, *, space_id: str, query_in: SpaceMemberQuery):
        target_dept_ids = None
        if query_in.department_id:
            if getattr(query_in, "is_direct", False):
                # 是否仅查直属部门
                target_dept_ids = [query_in.department_id]
            else:
                # 所有子孙部门
                sub_ids = self.dept_repo.get_all_sub_dept_ids(
                    space_id=space_id, root_dept_id=query_in.department_id
                )
                target_dept_ids = [query_in.department_id] + sub_ids

        query = self.repo.build_members_query(
            space_id=space_id,
            tab=query_in.tab,
            department_ids=target_dept_ids,
            keyword=query_in.keyword,
        )
        total = query.count()
        rows = query.offset(query_in.skip).limit(query_in.limit).all()

        member_ids = [m.id for m in rows]
        dept_map: dict[str, list[str]] = {mid: [] for mid in member_ids}

        if member_ids:
            dept_relations = (
                self.db.query(
                    SpaceDepartmentMember.space_member_id, SpaceDepartment.name
                )
                .join(
                    SpaceDepartment,
                    SpaceDepartment.id == SpaceDepartmentMember.department_id,
                )
                .filter(SpaceDepartmentMember.space_member_id.in_(member_ids))
                .all()
            )

            for mid, dept_name in dept_relations:
                dept_map[mid].append(dept_name)

        items = [
            SpaceMemberItemResponse(
                id=r.id,
                user=UserBrief(
                    id=r.user.id,
                    username=r.user.username,
                    nickname=r.user.nickname,
                    avatar=r.user.avatar,
                ),
                role=r.role,
                created_at=r.created_at,
                deleted_at=r.deleted_at,
                department_names=dept_map[r.id],
            )
            for r in rows
        ]
        active_count = self._get_deparment_active_member_count(
            space_id=space_id, department_id=query_in.department_id
        )
        has_more = (query_in.skip + len(items)) < total
        # 列表追加该部门的在职人数
        return SpaceMemberListResponse(
            items=items,
            total=total,
            has_more=has_more,
            page=query_in.page,
            page_size=query_in.page_size,
            extra=SpaceMemberExtra(active_member_count=active_count),
        )

    def _sync_member_departments(self, *, space_member_id: str, dept_ids: list[str]):
        self.db.query(SpaceDepartmentMember).filter(
            SpaceDepartmentMember.space_member_id == space_member_id
        ).delete()
        for dept_id in dept_ids:
            self.db.add(
                SpaceDepartmentMember(
                    space_member_id=space_member_id, department_id=dept_id
                )
            )

    def add_or_restore_member(self, *, space_id: str, data: SpaceMemberAdd):
        existing = self.repo.get_any_by_space_and_user(
            space_id=space_id, user_id=data.user_id
        )
        if existing:
            if existing.deleted_at is None:
                # 如果是外部联系人->成员/admin
                if existing.role == SpaceMemberRole.EXTERNAL and data.role != SpaceMemberRole.EXTERNAL:
                    existing.role = data.role
                    member = existing
                else:   
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST, detail="该成员已在空间中"
                    )
            else:
                # 软删除直接恢复
                existing.deleted_at = None
                existing.role = data.role
                member = existing
        else:
            member = SpaceMember(
                space_id=space_id,
                user_id=data.user_id,
                role=data.role,
            )
            self.db.add(member)
            self.db.flush()
        target_dept_ids = data.department_ids
        # 如果没有指定部门id，且默认加入根部门
        if not target_dept_ids:
            root_dept = self.dept_repo.get_root_dept_by_space_id(space_id=space_id)
            if root_dept:
                target_dept_ids = [root_dept.id]
        # 关联表同步
        if target_dept_ids:
            self._sync_member_departments(
                space_member_id=member.id, dept_ids=target_dept_ids
            )
        self.db.commit()
        return member



    def transfer_owner(
        self,
        *,
        space_id: str,
        current_owner_user_id: int,
        target_user_id: int,
        exit_space: bool = False,
        target_role_if_stay: SpaceMemberRole = SpaceMemberRole.ADMIN,
    ) -> Optional[bool]:
        """空间转让（仅所有者可发起）"""
        if current_owner_user_id == target_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="不能转让给自己"
            )
        space = self.db.query(Space).filter(Space.id == space_id).first()
        if not space:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到该空间")
        if space.owner_id != current_owner_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="您不是该空间的拥有者,无权进行转让"
            )

        target_member = self.repo.get_active_by_space_and_user(
            space_id=space_id, user_id=target_user_id
        )

        if not target_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="目标用户不是该空间在职成员，无法转让"
            )
        if target_member.role == SpaceMemberRole.EXTERNAL:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="无法转让给外部临时联系人"
            )

        current_owner_member = self.repo.get_active_by_space_and_user(
            space_id=space_id, user_id=current_owner_user_id
        )
        target_member.role = SpaceMemberRole.OWNER
        # 替换空间所有者
        space.owner_id = target_user_id
        # 处理转交人员的后续操作
        if exit_space:
            current_owner_member.soft_delete()
            # 清除中间表的关联记录
            self.db.query(SpaceDepartmentMember).filter(
                SpaceDepartmentMember.space_member_id == current_owner_member.id
            ).delete(synchronize_session=False)
        else:
            # 不退出空间，则修改成为指定的角色
            current_owner_member.role = target_role_if_stay
        self.db.commit()
        return True

    def operate_resigned(self, *, space_id: str, member_id: str):
        """离职办理"""
        member = self.repo.get_active_by_id(member_id=member_id)
        if not member or member.space_id != space_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到该成员")
        # 空间拥有者
        if member.role == SpaceMemberRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="空间所有者不能直接办理离职或退出，请先转让空间所有权",
            )
        member.soft_delete()

        self.db.commit()
        return True

    def batch_hard_delete_resigned(self, *, space_id: str, member_ids: list[str]):
        """已离职列表的物理删除"""
        if not member_ids:
            return True
        members = (
            self.db.query(SpaceMember)
            .filter(SpaceMember.space_id == space_id, SpaceMember.id.in_(member_ids))
            .all()
        )
        user_ids = [
            member.user_id for member in members if member.role != SpaceMemberRole.OWNER
        ]
        # 成员彻底删除需要清除相关协同的授权记录
        self.resource_grant_service.clear_user_grants_in_space(
            space_id=space_id, user_ids=user_ids
        )

        self.db.query(SpaceDepartmentMember).filter(
            SpaceDepartmentMember.space_member_id.in_(member_ids)
        ).delete(synchronize_session=False)
        self.db.query(SpaceMember).filter(
            SpaceMember.space_id == space_id, SpaceMember.id.in_(member_ids)
        ).delete(synchronize_session=False)
        self.db.commit()
        return True

    def adjust_departments(
        self, *, space_id: str, member_id: str, department_ids: list[str]
    ):
        """人员部门调整"""
        member = self.repo.get_active_by_id(member_id)
        if not member or member.space_id != space_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="成员不存在")

        # 如果没有指定部门id，则默认加入根部门
        target_ids = department_ids
        if not target_ids:
            root_dept = self.dept_repo.get_root_dept_by_space_id(space_id=space_id)
            if root_dept:
                target_ids = [root_dept.id]

        self._sync_member_departments(space_member_id=member_id, dept_ids=target_ids)
        self.db.commit()
        return True

    def update_role(self, *, space_id: str, member_id: str, new_role: SpaceMemberRole):
        member = self.repo.get_active_by_id(member_id)
        if not member or member.space_id != space_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="成员不存在")
        if new_role == SpaceMemberRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能直接设置为空间所有者，请先联系所有者走转让流程",
            )
        if member.role == SpaceMemberRole.OWNER and new_role != SpaceMemberRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="空间所有者不能直接降级"
            )
        member.role = new_role
        self.db.commit()
        return member

    def ensure_member_role(
        self,
        *,
        space_id: str,
        user_id: int,
        allow_roles: Sequence[SpaceMemberRole] | SpaceMemberRole | None = None,
        detail_message: str | None = None,
    ) -> SpaceMember:
        """校验团队成员以及角色权限"""
        member = self.get_member_by_user_id(space_id=space_id, user_id=user_id)
        if member is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="你不是空间成员")
        if allow_roles is not None:
            allowed_set = to_enum_values(allow_roles)
            if to_enum_value(member.role) not in allowed_set:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=detail_message or "你无权执行此操作",
                )
        return member
