"""sync schema drift space collect permission

Revision ID: e5a743231c72
Revises: 4a10a73e9538
Create Date: 2026-09-17 18:34:09.342996

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e5a743231c72"
down_revision: Union[str, None] = "4a10a73e9538"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    op.add_column(
        "space",
        sa.Column(
            "public_area_slug", sa.String(64), nullable=True, comment="公共区域短链"
        ),
    )
    op.create_unique_constraint(
        "uq_space_public_area_slug", "space", ["public_area_slug"]
    )
    op.alter_column(
        "knowledge_base",
        "team_id",
        existing_type=sa.String(length=36),
        nullable=True,
        comment="所属团队（允许为空:个人空间或者公共区）",
    )
    op.alter_column(
        "knowledge_base",
        "user_id",
        existing_type=sa.Integer(),
        nullable=True,
        comment="v2使用creator_id",
    )
    op.alter_column(
        "permission_groups",
        "role",
        existing_type=sa.Integer(),
        nullable=True,
        comment="旧角色整数，V2采用role_key了",
    )
    op.alter_column(
        "permission_groups",
        "target_type",
        existing_type=sa.String(length=30),
        nullable=True,
        comment="旧目标类型，V2 使用 scope_type",
    )
    op.alter_column(
        "permission_groups",
        "target_id",
        existing_type=sa.String(length=36),
        nullable=True,
        comment="旧目标ID，V2 使用 scope_id",
    )

    op.add_column(
        "collect",
        sa.Column(
            "target_type", sa.String(length=20), nullable=True, comment="目标资源类型"
        ),
    )
    op.add_column(
        "collect",
        sa.Column(
            "target_id", sa.String(length=36), nullable=True, comment="目标资源ID"
        ),
    )
    conn.execute(
        sa.text(
            """
            UPDATE collect
            SET target_type = 'knowledge',
                target_id = knowledge_id
            WHERE knowledge_id IS NOT NULL
              AND document_id IS NULL
              AND target_id IS NULL
            """
        )
    )
    conn.execute(
        sa.text(
            """
            UPDATE collect
            SET target_type = 'document',
                target_id = document_id
            WHERE document_id IS NOT NULL
              AND target_id IS NULL
            """
        )
    )
    # 兜底：仍空则用旧 resource_type + 任一 id
    conn.execute(
        sa.text(
            """
            UPDATE collect
            SET target_type = COALESCE(resource_type, target_type),
                target_id = COALESCE(target_id, document_id, knowledge_id)
            WHERE target_id IS NULL
            """
        )
    )

    op.alter_column(
        "collect",
        "target_type",
        existing_type=sa.String(length=20),
        nullable=False,
    )
    op.alter_column(
        "collect",
        "target_id",
        existing_type=sa.String(length=36),
        nullable=False,
    )

    # 旧列：代码不再写，先可空避免新 INSERT 炸
    op.alter_column(
        "collect",
        "resource_type",
        existing_type=sa.String(length=20),
        nullable=True,
        comment="旧资源类型，V2 使用 target_type",
    )

    op.create_unique_constraint(
        "uq_collect_user_target",
        "collect",
        ["user_id", "target_id", "target_type"],
    )


def downgrade() -> None:
    # 本地可不跑；需要时可按逆序还原
    op.drop_constraint("uq_collect_user_target", "collect", type_="unique")
    op.drop_column("collect", "target_id")
    op.drop_column("collect", "target_type")

    op.alter_column(
        "collect",
        "resource_type",
        existing_type=sa.String(length=20),
        nullable=False,
    )

    op.alter_column(
        "permission_groups",
        "target_id",
        existing_type=sa.String(length=36),
        nullable=False,
    )
    op.alter_column(
        "permission_groups",
        "target_type",
        existing_type=sa.String(length=30),
        nullable=False,
    )
    op.alter_column(
        "permission_groups",
        "role",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.alter_column(
        "knowledge_base",
        "user_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.alter_column(
        "knowledge_base",
        "team_id",
        existing_type=sa.String(length=36),
        nullable=False,
    )

    op.drop_constraint("uq_space_public_area_slug", "space", type_="unique")
    op.drop_column("space", "public_area_slug")
