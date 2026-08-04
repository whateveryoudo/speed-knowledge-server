from sqlalchemy import (
    Column,
    String,
    DateTime,
    UniqueConstraint,
    Integer,
    ForeignKey,
)
from app.db.base import Base
import uuid
from datetime import datetime
from sqlalchemy.sql import func
from app.common.enums.resource_grant import PrincipalRole


class ResourceGrant(Base):
    __tablename__ = "resource_grant"
    __table_args__ = (
        UniqueConstraint(
            "resource_type",
            "resource_id",
            "principal_type",
            "principal_id",
            "principal_role",
            name="uniq_resource_grant",
        ),
    )
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    resource_type = Column[str](
        String(30),
        nullable=False,
        comment="资源类型,knowledge:知识库,document:文档",
    )

    resource_id = Column[str](
        String(36),
        nullable=False,
        comment="资源ID",
    )

    principal_type = Column[str](
        String(30),
        nullable=False,
        comment="主体类型,user:用户,space_role:空间角色,team_role:团队角色",
    )

    principal_id = Column[str](
        String(36),
        nullable=False,
        comment="主体ID",
    )

    principal_role = Column[str](
        String(30),
        nullable=False,
        comment="用户在空间或团队中的身份(这里是一个不固定的角色)",
    )

    resource_role = Column[str](
        String(30),
        nullable=False,
        comment="这个主体对知识库有什么权限",
    )

    source = Column[str](
        String(30),
        nullable=False,
        comment="授权来源,creator:创建者,default_policy:默认策略,direct:直接授权,invitation:邀请",
    )
    created_by = Column[int](
        Integer,
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
        comment="授权操作人",
    )
    created_at = Column[datetime](
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        comment="创建时间",
    )

    updated_at = Column[datetime](
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),
        comment="更新时间",
    )
