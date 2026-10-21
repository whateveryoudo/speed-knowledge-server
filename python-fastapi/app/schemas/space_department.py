from pydantic import BaseModel, Field, ConfigDict


class SpaceDepartmentCreate(BaseModel):
    parent_id: str | None = Field(None, description="上级部门ID,根节点是null")
    name: str = Field(..., max_length=100, description="部门名称")
    sort_order: int = Field(default=0, description="排序")


class SpaceDepartmentUpdate(BaseModel):
    name: str = Field(..., max_length=100, description="部门名称")
    sort_order: int = Field(default=0, description="排序")
    parent_id: str | None = Field(None, description="上级部门ID,根节点是null")


class SpaceDepartmentTreeItem(BaseModel):
    id: str = Field(..., description="部门ID")
    space_id: str=Field(...,description="空间ID")
    parent_id: str | None = Field(None, description="上级部门ID,根节点是null")
    name: str = Field(..., max_length=100, description="部门名称")
    sort_order: int = Field(default=0, description="排序")
    children: list["SpaceDepartmentTreeItem"] = Field(default_factory=list)
    has_children:bool = Field(default=False, description="树懒加载可用于前端是否再显示下级")