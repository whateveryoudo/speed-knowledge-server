from collections.abc import Sequence
from app.models.space_department import SpaceDepartment
from typing import Optional
from sqlalchemy.orm import aliased, Session
from app.models.space_department import SpaceDepartmentMember
from sqlalchemy import exists, select


class SpaceDepartmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, *, space_id: str, dept_id: str) -> Optional[SpaceDepartment]:
        """通过id获取部门"""
        return (
            self.db.query(SpaceDepartment)
            .filter(
                SpaceDepartment.id == dept_id,
                SpaceDepartment.space_id == space_id,
            )
            .first()
        )

    def get_by_ids(
        self, *, space_id: str, dept_ids: list[str]
    ) -> list[SpaceDepartment]:
        """通过ids获取部门列表"""
        if not dept_ids:
            return []
        return (
            self.db.query(SpaceDepartment)
            .filter(
                SpaceDepartment.id.in_(dept_ids),
                SpaceDepartment.space_id == space_id,
            )
            .all()
        )

    def has_external_children(self, *, space_id: str, dept_ids: list[str]) -> bool:
        """查询是否包含子部门未删除"""
        if not dept_ids:
            return False
        return self.db.query(
            exists().where(
                SpaceDepartment.parent_id.in_(dept_ids),
                SpaceDepartment.id.not_in_(dept_ids),
                SpaceDepartment.space_id == space_id,
            )
        ).scalar()

    def get_root_dept_by_space_id(self, *, space_id: str) -> Optional[SpaceDepartment]:
        """通过空间ID获取根部门"""
        return (
            self.db.query(SpaceDepartment)
            .filter(
                SpaceDepartment.space_id == space_id,
                SpaceDepartment.parent_id.is_(None),
            )
            .first()
        )

    def get_all_by_space(self, *, space_id: str) -> Sequence[SpaceDepartment]:
        """查询空间下所有部门"""
        return (
            self.db.query(SpaceDepartment)
            .filter(SpaceDepartment.space_id == space_id)
            .order_by(
                SpaceDepartment.sort_order.asc(), SpaceDepartment.created_at.asc()
            )
            .all()
        )

    def get_children_with_has_child_flag(
        self,
        *,
        space_id: str,
        parent_id: str | None = None,
    ) -> list[tuple[SpaceDepartment, bool]]:
        """查询带有has_children标识的子部门列表"""
        sub_dept = aliased(SpaceDepartment)
        has_children_expr = exists(
            select(1).where(sub_dept.parent_id == SpaceDepartment.id)
        ).label("has_children")
        query = (
            self.db.query(SpaceDepartment, has_children_expr)
            .filter(SpaceDepartment.space_id == space_id)
            .order_by(
                SpaceDepartment.sort_order.asc(), SpaceDepartment.created_at.asc()
            )
        )
        if parent_id is not None:
            query = query.filter(SpaceDepartment.parent_id == parent_id)
        else:
            query = query.filter(SpaceDepartment.parent_id.is_(None))
        return query.all()

    def get_all_sub_dept_ids(self, *, space_id: str, root_dept_id: str) -> list[str]:
        """BFS广度优先搜索：某个部门名下所有子孙部门ID"""
        all_depts = (
            self.db.query(SpaceDepartment.id, SpaceDepartment.parent_id)
            .filter(SpaceDepartment.space_id == space_id)
            .all()
        )
        tree_map: dict[str | None, list[str]] = {}
        for did, pid in all_depts:
            tree_map.setdefault(pid, []).append(did)

        result: list[str] = []
        queue = [root_dept_id]
        while queue:
            cur = queue.pop(0)
            for child_id in tree_map.get(cur, []):
                result.append(child_id)
                queue.append(child_id)
        return result

    def has_children(self, *, space_id: str, dept_id: str) -> bool:
        """判断某个部门是否有子部门"""
        return (
            self.db.query(SpaceDepartment.id)
            .filter(
                SpaceDepartment.parent_id == dept_id,
                SpaceDepartment.space_id == space_id,
            )
            .first()
            is not None
        )

    def create(
        self,
        *,
        space_id: str,
        name: str,
        parent_id: str | None = None,
        sort_order: int = 0,
        flush: bool = False,
    ) -> SpaceDepartment:
        """创建空间部门"""
        dept = SpaceDepartment(
            space_id=space_id,
            name=name,
            parent_id=parent_id,
            sort_order=sort_order,
        )
        self.db.add(dept)
        if flush:
            self.db.flush()
        return dept

    def clear_departments_members(self, *, dept_ids: list[str]):
        """批量清空部门下所有成员管理关系"""
        if not dept_ids:
            return
        self.db.query(SpaceDepartmentMember).filter(
            SpaceDepartmentMember.department_id.in_(dept_ids)
        ).delete(synchronize_session=False)

    def clear_department_members(self, *, dept_id: str):
        """清空部门下所有成员管理关系"""
        self.db.query(SpaceDepartmentMember).filter(
            SpaceDepartmentMember.department_id == dept_id
        ).delete(synchronize_session=False)

    def batch_delete(self, *, dept_ids: list[str]):
        """批量删除部门"""
        if not dept_ids:
            return
        self.db.query(SpaceDepartment).filter(
            SpaceDepartment.id.in_(dept_ids)
        ).delete(synchronize_session=False)

    def delete(self, dept: SpaceDepartment):
        """删除实体"""
        self.db.delete(dept)


