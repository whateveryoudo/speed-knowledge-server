"""知识库分组表结构修改,已有数据迁移

Revision ID: cd719dbf683b
Revises: 7cb491d679b6
Create Date: 2026-09-30 17:33:41.039437

"""
from sqlalchemy import table
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "cd719dbf683b"
down_revision: Union[str, None] = "7cb491d679b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "knowledge_group",
        sa.Column(
            "scope_type",
            sa.String(length=20),
            nullable=True,
            comment="容器类型: personal, team, space",
        ),
    )

    op.add_column(
        "knowledge_group",
        sa.Column("scope_id", sa.String(length=64), nullable=True, comment="容器id"),
    )

    op.add_column(
        "knowledge_group",
        sa.Column("created_by", sa.Integer(), nullable=True, comment="创建者id"),
    )
    # 数据回填
    conn = op.get_bind()

    # 团队知识库分组回填

    conn.execute(
        sa.text(
            """
        UPDATE knowledge_group SET scope_type = 'team', scope_id = team_id, created_by = user_id WHERE team_id IS NOT NULL AND team_id != ''
        """
        )
    )

    # 个人知识库分组回填

    conn.execute(
        sa.text(
            """
        UPDATE knowledge_group SET scope_type = 'personal', scope_id = CAST(user_id AS CHAR),created_by = user_id WHERE team_id IS NULL OR team_id = ''
        """
        )
    )
    # 收紧字段约束

    op.alter_column(
        "knowledge_group",
        "scope_type",
        existing_type=sa.String(length=20),
        nullable=False,
    )

    op.alter_column(
        "knowledge_group",
        "scope_id",
        existing_type=sa.String(length=36),
        nullable=False,
    )

    # 创建索引
    op.create_index(
        "ix_knowledge_group_scope",
        "knowledge_group",
        ["scope_type", "scope_id"],
        unique=False,
    )

    op.create_index(
        "ix_knowledge_group_created_by",
        "knowledge_group",
        ["created_by"],
        unique=False,
    )
    # 删除旧列和索引
    op.drop_index("ix_knowledge_group_team_id", table_name="knowledge_group")
    op.drop_index("ix_knowledge_group_user_id", table_name="knowledge_group")
    op.drop_column(
        "knowledge_group",
        "team_id",
    )
    op.drop_column("knowledge_group", "user_id")


def downgrade() -> None:
    op.add_column(
        "knowledge_group",
        sa.Column("team_id", sa.Integer(), nullable=True, comment="团队ID"),
    )

    op.add_column(
        "knowledge_group",
        sa.Column("user_id", sa.Integer(), nullable=True, comment="用户ID"),
    )

    conn = op.get_bind()

    conn.execute(
        sa.text(
            """
            UPDATE knowledge_group SET team_id = scope_id, user_id = created_by WHERE scope_type = 'team'
            """
        )
    )

    conn.execute(
        sa.text(
            """
            UPDATE knowledge_group SET team_id = NULL,user_id = CAST(scope_id AS SIGNED) WHERE scope_type = 'personal'
            """
        )
    )
    op.create_index(
        "ix_knowledge_group_user_id", "knowledge_group", ["user_id"], unique=False
    )
    op.create_index(
        "ix_knowledge_group_team_id", "knowledge_group", ["team_id"], unique=False
    )
    op.drop_index("ix_knowledge_group_scope", table_name="knowledge_group")
    op.drop_index("ix_knowledge_group_created_by", table_name="knowledge_group")
    op.drop_column("knowledge_group", "scope_type")
    op.drop_column("knowledge_group", "scope_id")
    op.drop_column("knowledge_group", "created_by")
