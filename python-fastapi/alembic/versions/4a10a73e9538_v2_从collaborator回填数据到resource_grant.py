"""v2 从collaborator回填数据到resource_grant

Revision ID: 4a10a73e9538
Revises: 254b5f4dcdb0
Create Date: 2026-09-15 18:57:20.064540
说明：
- 幂等回填 resource_grant
- 不删旧表/旧列
- pending 协作者默认丢弃
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4a10a73e9538"
down_revision: Union[str, None] = "254b5f4dcdb0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    # 已有协作者  status=2 ACCEPTED role:1->read, 2->edit, 3->admin; source: 0->creator, 1-> invitation,2->direct
    conn.execute(
        sa.text(
            """
        INSERT INTO resource_grant(
        id,
        resource_type,
        resource_id,
        principal_type,
        principal_id,
        principal_role,
        resource_role,
        source,
        created_by,
        created_at,
        updated_at
        )
        SELECT
            UUID(),
            c.target_type,
            CASE
                WHEN c.target_type = 'knowledge' THEN c.knowledge_id
                WHEN c.target_type = 'document' THEN c.document_id
                ELSE COALESCE(c.knowledge_id, c.document_id)
            END AS resource_id,
            'user',
            CAST(c.user_id AS CHAR),
            'none',
            CASE c.role
                WHEN 1 THEN 'read'
                WHEN 2 THEN 'edit'
                WHEN 3 THEN 'admin'
                ELSE 'read'
            END,
            CASE c.source
                WHEN 0 THEN 'creator'    
                WHEN 1 THEN 'invitation'    
                WHEN 2 THEN 'direct'   
                ELSE 'direct'
            END,
            c.user_id,
            c.created_at,
            c.updated_at

        FROM collaborator c 
        WHERE c.status = 2
        AND (
            (c.target_type = 'knowledge' AND c.knowledge_id IS NOT NULL)
            OR (c.target_type = 'document' AND c.document_id IS NOT NULL)
            OR (c.target_type NOT IN ('knowledge', 'document') AND COALESCE(c.knowledge_id, c.document_id) IS NOT NULL)
        )
        ON DUPLICATE KEY UPDATE
            resource_role = VALUES(resource_role),
            source = VALUES(source),
            updated_at = VALUES(updated_at)
        """
        )
    )

    # 知识库创建者兜底grant （防止collaborator 漏掉 creator）

    conn.execute(
        sa.text(
            """
            INSERT INTO resource_grant(
            id,
            resource_type,
            resource_id,
            principal_type,
            principal_id,
            principal_role,
            resource_role,
            source,
            created_by
            )
            SELECT
                UUID(),
                'knowledge',
                k.id,
                'user',
                CAST(k.creator_id AS CHAR),
                'none',
                'admin',
                'creator',
                k.creator_id
            FROM knowledge_base k    
            WHERE k.deleted_at IS NULL AND k.creator_id IS NOT NULL
            ON DUPLICATE KEY UPDATE
                resource_role = 'admin',
                source = 'creator',
                updated_at = CURRENT_TIMESTAMP
        """
        )
    )


def downgrade() -> None:
    pass
