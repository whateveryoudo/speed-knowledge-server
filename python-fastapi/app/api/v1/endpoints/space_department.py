from app.schemas.space_department import (
    SpaceDepartmentCreate,
    SpaceDepartmentUpdate
)
from app.services.space_member_service import SpaceMemberService
from app.services.space_department_service import SpaceDepartmentService
from fastapi import APIRouter, Depends, Query, HTTPException, status
from app.models.space import Space
from app.models.space_member import SpaceMember
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_space, require_space_admin

router = APIRouter()


@router.get("/tree")
def get_department_tree(
    space: Space = Depends(get_current_space),
    db: Session = Depends(get_db),
):
    """全量部门树"""
    return SpaceDepartmentService(db).get_all_tree_departments(space_id=space.id)


@router.get("/tree/lazy")
def get_department_lazy_tree(
    parent_id: str | None = Query(None, description="父部门ID"),
    db: Session = Depends(get_db),
    space: Space = Depends(get_current_space),
):
    """懒加载部门树"""
    return SpaceDepartmentService(db).get_lazy_tree_departments(space_id=space.id, parent_id=parent_id)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_department(
    data: SpaceDepartmentCreate,
    space: Space = Depends(get_current_space),
    admin_member: SpaceMember = Depends(require_space_admin),
    db: Session = Depends(get_db),
):
    """新建部门"""
    return SpaceDepartmentService(db).create_department(space_id=space.id, data=data)

@router.put("/{dept_id}")
def update_department(
    dept_id: str,
    data: SpaceDepartmentUpdate,
    space: Space = Depends(get_current_space),
    admin_member: SpaceMember = Depends(require_space_admin),
    db: Session = Depends(get_db),
):
    """修改部门信息：重命名、排序、调整上级部门"""
    return SpaceDepartmentService(db).update_department(
        space_id=space.id, dept_id=dept_id, data=data
    )


@router.delete("/{dept_id}")
def delete_department(
    dept_id: str,
    space: Space = Depends(get_current_space),
    admin_member: SpaceMember = Depends(require_space_admin),
    db: Session = Depends(get_db),
):
    """删除部门"""
    return SpaceDepartmentService(db).delete_department(
        space_id=space.id, dept_id=dept_id
    )
