"""知识库分组表结构修改,已有数据迁移

Revision ID: cd719dbf683b
Revises: 7cb491d679b6
Create Date: 2026-09-30 17:33:41.039437

"""
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


def downgrade() -> None:
    pass
