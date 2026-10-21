from app.schemas.space_department import SpaceDepartmentTreeItem
from sqlalchemy.orm.session import Session
from app.models.space_department import SpaceDepartment
from sqlalchemy.orm import aliased
from sqlalchemy import exists, select
from app.schemas.space_department import SpaceDepartmentCreate, SpaceDepartmentUpdate
from app.repositories.space_department_repository import SpaceDepartmentRepository
from fastapi import HTTPException, status


class SpaceDepartmentService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = SpaceDepartmentRepository(db)

    def create_root_department(self, *, space_id: str, name: str) -> SpaceDepartment:
        """默认部门创建（新建空间的时候创建默认部门）"""
        return self.repo.create(
            space_id=space_id, name=name, parent_id=None, sort_order=0, flush=True
        )

    def get_all_tree_departments(
        self, *, space_id: str
    ) -> list[SpaceDepartmentTreeItem]:
        """获取树形部门数据"""
        # 获取所有部门
        all_depts = self.repo.get_all_by_space(space_id=space_id)
        if not all_depts:
            return []

        parent_id_set = {d.parent_id for d in all_depts if d.parent_id is not None}
        node_map = {
            d.id: SpaceDepartmentTreeItem(
                id=d.id,
                name=d.name,
                space_id=d.space_id,
                sort_order=d.sort_order,
                parent_id=d.parent_id,
                has_children=d.id in parent_id_set,
                children=[],
            )
            for d in all_depts
        }
        # 树结构组装
        tree: list[SpaceDepartmentTreeItem] = []
        for d in all_depts:
            node = node_map[d.id]
            if d.parent_id and d.parent_id in node_map:
                node_map[d.parent_id].children.append(node)
            else:
                tree.append(node)
        return tree

    def get_lazy_tree_departments(
        self,
        *,
        space_id: str,
        parent_id: str | None = None,
    ) -> list[SpaceDepartmentTreeItem]:
        """获取树形部门数据（懒加载）"""
        rows = self.repo.get_children_with_has_child_flag(
            space_id=space_id, parent_id=parent_id
        )
        return [
            SpaceDepartmentTreeItem(
                id=dept.id,
                name=dept.name,
                space_id=dept.space_id,
                sort_order=dept.sort_order,
                parent_id=dept.parent_id,
                has_children=has_children,
                children=[],
            )
            for (dept, has_children) in rows
        ]

    def create_department(self, *, space_id: str, data: SpaceDepartmentCreate):
        """部门创建"""
        if data.parent_id:
            parent = self.repo.get_by_id(
                space_id=space_id,
                dept_id=data.parent_id,
            )
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="父部门不存在"
                )
        dept = self.repo.create(
            space_id=space_id,
            name=data.name,
            parent_id=data.parent_id,
            sort_order=data.sort_order,
        )
        self.db.commit()
        return dept

    def update_department(
        self, *, space_id: str, dept_id: str, data: SpaceDepartmentUpdate
    ) -> SpaceDepartment:
        """部门更新（支持切换部门，这里会进行闭环检测）"""
        dept = self.repo.get_by_id(
            space_id=space_id,
            dept_id=dept_id,
        )
        if not dept:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="部门不存在")
        if dept.parent_id is None and data.parent_id is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="根部门不能设置为子部门"
            )

        # 防环检测

        if data.parent_id is not None and data.parent_id != dept.parent_id:
            if data.parent_id == dept_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="不能将上级部门设置为自身"
                )
            all_sub_ids = self.repo.get_all_sub_dept_ids(
                space_id=space_id, root_dept_id=dept_id
            )
            if data.parent_id in all_sub_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="不能将子孙部门设置为上级部门"
                )
            dept.parent_id = data.parent_id

        if data.name:
            dept.name = data.name.strip()
        if data.sort_order is not None:
            dept.sort_order = data.sort_order

        self.db.commit()
        return dept

    def delete_department(self, *, space_id: str, dept_id: str) -> None:
        """部门删除"""
        dept = self.repo.get_by_id(
            space_id=space_id,
            dept_id=dept_id,
        )
        if not dept:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="部门不存在")

        if dept.parent_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="根部门不能删除"
            )
        if self.repo.has_children(space_id=space_id,dept_id=dept_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="部门还有子部门，不能删除"
            )
        self.repo.clear_department_members(dept_id=dept_id)
        self.repo.delete(dept)
        self.db.commit()
        return True
