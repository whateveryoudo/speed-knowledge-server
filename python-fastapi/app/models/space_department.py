from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from sqlalchemy import String, ForeignKey, Integer, DateTime
from datetime import datetime
from typing import Optional
from sqlalchemy.schema import UniqueConstraint
import uuid


class SpaceDepartment(Base):
    """部门模型树"""

    __tablename__ = "space_department"
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    space_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("space.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    parent_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("space_department.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="部门名称")
    sort_order: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="排序"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
    )

    parent = relationship(
        "SpaceDepartment", remote_side=[id], back_populates="children"
    )
    children = relationship("SpaceDepartment", back_populates="parent")

    department_members = relationship(
        "SpaceDepartmentMember",
        back_populates="department",
        cascade="all,delete-orphan",
    )


class SpaceDepartmentMember(Base):
    """部门和成员多对多中间表"""

    __tablename__ = "space_department_member"
    __table_args__ = (
        UniqueConstraint(
            "department_id", "space_member_id", name="uq_dept_space_member"
        ),
    )
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    department_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("space_department.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    space_member_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("space_member.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
    )
    department = relationship("SpaceDepartment", back_populates="department_members")
    space_member = relationship("SpaceMember", back_populates="department_relations")
