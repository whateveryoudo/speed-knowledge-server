"""v2 数据回填权限列

Revision ID: 254b5f4dcdb0
Revises: f85b5aac6c6e
Create Date: 2026-09-14 18:47:59.369200

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "254b5f4dcdb0"
down_revision: Union[str, None] = "f85b5aac6c6e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    conn.execute(
        sa.text(
            """
            UPDATE knowledge_base SET creator_id = user_id WHERE creator_id IS NULL AND user_id IS NOT NULL
            """
        )
    )

    conn.execute(
        sa.text(
            """UPDATE knowledge_base SET visibility = CASE WHEN is_public = 1 THEN 'public' ELSE 'private' END"""
        )
    )

    conn.execute(
        sa.text(
            """UPDATE document_base SET visibility = CASE WHEN is_public = 1 THEN 'public' ELSE 'inherit' END"""
        )
    )

    conn.execute(
        sa.text(
            """
    UPDATE permission_groups 
    SET 
        scope_type = target_type,
        scope_id = target_id,
        role_key = CASE role
            WHEN 1 THEN 'read'
            WHEN 2 THEN 'edit'
            WHEN 3 THEN 'admin'
            ELSE CAST(role AS CHAR)
        END
    WHERE scope_id IS NULL
    """
        )
    )

    conn.execute(sa.text("""
    UPDATE permission_abilities
    SET enabled = enable
    """))

    op.alter_column('knowledge_base',"creator_id",existing_type=sa.Integer(), nullable = False)
    op.alter_column('permission_groups',"role_key",existing_type=sa.String(30), nullable = False)
    op.alter_column('permission_groups',"scope_type",existing_type=sa.String(30), nullable = False)
    op.alter_column('permission_groups',"scope_id",existing_type=sa.String(36), nullable = False)


def downgrade() -> None:
    pass
