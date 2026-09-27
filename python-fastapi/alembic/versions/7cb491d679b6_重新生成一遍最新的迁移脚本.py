"""重新生成一遍最新的迁移脚本

Revision ID: 7cb491d679b6
Revises: 6c40e3591b43
Create Date: 2026-09-27 11:10:51.000483

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '7cb491d679b6'
down_revision: Union[str, None] = '6c40e3591b43'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def safe_drop_foreign_key(table_name: str, fk_name: str = None, column_name: str = None):
    """安全/幂等删除外键约束：存在则删，不存在静默跳过"""
    conn = op.get_bind()
    if not fk_name and column_name:
        res = conn.execute(sa.text("""
            SELECT CONSTRAINT_NAME 
            FROM information_schema.KEY_COLUMN_USAGE 
            WHERE TABLE_SCHEMA = DATABASE() 
              AND TABLE_NAME = :table 
              AND COLUMN_NAME = :col 
              AND REFERENCED_TABLE_NAME IS NOT NULL
        """), {"table": table_name, "col": column_name}).fetchall()
        for row in res:
            op.drop_constraint(row[0], table_name, type_='foreignkey')
        return

    if fk_name:
        res = conn.execute(sa.text("""
            SELECT CONSTRAINT_NAME 
            FROM information_schema.TABLE_CONSTRAINTS 
            WHERE TABLE_SCHEMA = DATABASE() 
              AND TABLE_NAME = :table 
              AND CONSTRAINT_NAME = :fk 
              AND CONSTRAINT_TYPE = 'FOREIGN KEY'
        """), {"table": table_name, "fk": fk_name}).fetchone()
        if res:
            op.drop_constraint(fk_name, table_name, type_='foreignkey')


def safe_drop_index(index_name: str, table_name: str):
    """安全删除索引：存在则删，不存在跳过"""
    conn = op.get_bind()
    res = conn.execute(sa.text("""
        SELECT INDEX_NAME 
        FROM information_schema.STATISTICS 
        WHERE TABLE_SCHEMA = DATABASE() 
          AND TABLE_NAME = :table 
          AND INDEX_NAME = :idx
    """), {"table": table_name, "idx": index_name}).fetchone()
    if res:
        op.drop_index(index_name, table_name=table_name)


def safe_drop_column(table_name: str, column_name: str):
    """安全删除列：存在则删，不存在跳过"""
    conn = op.get_bind()
    res = conn.execute(sa.text("""
        SELECT COLUMN_NAME 
        FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = DATABASE() 
          AND TABLE_NAME = :table 
          AND COLUMN_NAME = :col
    """), {"table": table_name, "col": column_name}).fetchone()
    if res:
        op.drop_column(table_name, column_name)


def upgrade() -> None:
    # ### 1. 先安全清理历史遗留的外键约束与索引（防止阻碍后续 drop_column / drop_index） ###
    # 清理 invitation 表中可能依附在 document_id 上的旧外键与索引
    safe_drop_foreign_key('invitation', column_name='document_id')
    safe_drop_index('ix_invitation_document_id', 'invitation')
    
    # 清理 knowledge_group_relation 表中 user_id 的旧外键
    safe_drop_foreign_key('knowledge_group_relation', column_name='user_id')
    safe_drop_foreign_key('knowledge_group_relation', fk_name='knowledge_group_relation_ibfk_3')
    safe_drop_index('uix_user_knowledge', 'knowledge_group_relation')

    # ### 2. 执行结构变更 ###
    # 如果 collect 表的 user 外键不存在才创建，避免重复创建报错
    conn = op.get_bind()
    collect_fk = conn.execute(sa.text("""
        SELECT CONSTRAINT_NAME 
        FROM information_schema.KEY_COLUMN_USAGE 
        WHERE TABLE_SCHEMA = DATABASE() 
          AND TABLE_NAME = 'collect' 
          AND COLUMN_NAME = 'user_id' 
          AND REFERENCED_TABLE_NAME = 'user'
    """)).fetchone()
    if not collect_fk:
        op.create_foreign_key(None, 'collect', 'user', ['user_id'], ['id'], ondelete='CASCADE')

    safe_drop_column('knowledge_group_relation', 'user_id')
    op.alter_column('permission_abilities', 'ability_key',
               existing_type=mysql.VARCHAR(length=30),
               type_=sa.String(length=50),
               existing_comment='能力键',
               existing_nullable=False)
    op.alter_column('permission_abilities', 'created_at',
               existing_type=mysql.DATETIME(),
               nullable=False,
               existing_server_default=sa.text('(now())'))
    op.alter_column('permission_abilities', 'updated_at',
               existing_type=mysql.DATETIME(),
               nullable=False,
               existing_server_default=sa.text('(now())'))
    op.create_index(op.f('ix_permission_abilities_permission_group_id'), 'permission_abilities', ['permission_group_id'], unique=False)
    op.create_unique_constraint('uq_permission_ability_group_key', 'permission_abilities', ['permission_group_id', 'ability_key'])
    safe_drop_column('permission_abilities', 'enable')
    op.alter_column('permission_groups', 'role_key',
               existing_type=mysql.VARCHAR(length=30),
               comment='资源角色',
               existing_nullable=False)
    op.alter_column('permission_groups', 'scope_type',
               existing_type=mysql.VARCHAR(length=30),
               comment='作用域类型：knowledge/document/space/team',
               existing_nullable=False)
    op.alter_column('permission_groups', 'scope_id',
               existing_type=mysql.VARCHAR(length=36),
               comment='作用域ID',
               existing_nullable=False)
    op.alter_column('permission_groups', 'created_at',
               existing_type=mysql.DATETIME(),
               nullable=False,
               existing_server_default=sa.text('(now())'))
    op.alter_column('permission_groups', 'updated_at',
               existing_type=mysql.DATETIME(),
               nullable=False,
               existing_server_default=sa.text('(now())'))
    op.create_unique_constraint('uq_permission_group_scope_role', 'permission_groups', ['role_key', 'scope_type', 'scope_id'])
    safe_drop_column('permission_groups', 'target_id')
    safe_drop_column('permission_groups', 'role')
    safe_drop_column('permission_groups', 'target_type')
    safe_drop_index('idx_resource_grant_resource', 'resource_grant')
    op.alter_column('space', 'domain',
               existing_type=mysql.VARCHAR(charset='utf8mb4', collation='utf8mb4_0900_ai_ci', length=64),
               comment='空间域名,也用于标识访问(可选,个人类型可不传入domain)',
               existing_comment='空间域名,也用于标识访问(可选,个人类型可不传入domin)',
               existing_nullable=True)
    op.create_unique_constraint('uq_space_member_space_user', 'space_member', ['space_id', 'user_id'])
    safe_drop_column('space_member', 'deleted_at')
    op.alter_column('team_member', 'role',
               existing_type=mysql.ENUM('OWNER', 'ADMIN', 'MEMBER', 'EXTERNAL'),
               type_=sa.Enum('OWNER', 'ADMIN', 'MEMBER', 'READONLY', name='teammemberrole'),
               existing_comment='角色',
               existing_nullable=False)
    op.create_unique_constraint('uix_team_member_team_user', 'team_member', ['team_id', 'user_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('uix_team_member_team_user', 'team_member', type_='unique')
    op.alter_column('team_member', 'role',
               existing_type=sa.Enum('OWNER', 'ADMIN', 'MEMBER', 'READONLY', name='teammemberrole'),
               type_=mysql.ENUM('OWNER', 'ADMIN', 'MEMBER', 'EXTERNAL'),
               existing_comment='角色',
               existing_nullable=False)
    op.add_column('space_member', sa.Column('deleted_at', mysql.DATETIME(), nullable=True, comment='删除时间(NULL表示未删除)'))
    op.drop_constraint('uq_space_member_space_user', 'space_member', type_='unique')
    op.alter_column('space', 'domain',
               existing_type=mysql.VARCHAR(charset='utf8mb4', collation='utf8mb4_0900_ai_ci', length=64),
               comment='空间域名,也用于标识访问(可选,个人类型可不传入domin)',
               existing_comment='空间域名,也用于标识访问(可选,个人类型可不传入domain)',
               existing_nullable=True)
    op.create_index(op.f('idx_resource_grant_resource'), 'resource_grant', ['resource_type', 'resource_id'], unique=False)
    op.add_column('permission_groups', sa.Column('target_type', mysql.VARCHAR(length=30), nullable=True))
    op.add_column('permission_groups', sa.Column('role', mysql.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('permission_groups', sa.Column('target_id', mysql.VARCHAR(length=36), nullable=True))
    op.drop_constraint('uq_permission_group_scope_role', 'permission_groups', type_='unique')
    op.alter_column('permission_groups', 'updated_at',
               existing_type=mysql.DATETIME(),
               nullable=True,
               existing_server_default=sa.text('(now())'))
    op.alter_column('permission_groups', 'created_at',
               existing_type=mysql.DATETIME(),
               nullable=True,
               existing_server_default=sa.text('(now())'))
    op.alter_column('permission_groups', 'scope_id',
               existing_type=mysql.VARCHAR(length=36),
               comment=None,
               existing_comment='作用域ID',
               existing_nullable=False)
    op.alter_column('permission_groups', 'scope_type',
               existing_type=mysql.VARCHAR(length=30),
               comment=None,
               existing_comment='作用域类型：knowledge/document/space/team',
               existing_nullable=False)
    op.alter_column('permission_groups', 'role_key',
               existing_type=mysql.VARCHAR(length=30),
               comment=None,
               existing_comment='资源角色',
               existing_nullable=False)
    op.add_column('permission_abilities', sa.Column('enable', mysql.TINYINT(display_width=1), server_default=sa.text("'0'"), autoincrement=False, nullable=False, comment='是否启用'))
    op.drop_constraint('uq_permission_ability_group_key', 'permission_abilities', type_='unique')
    op.drop_index(op.f('ix_permission_abilities_permission_group_id'), table_name='permission_abilities')
    op.alter_column('permission_abilities', 'updated_at',
               existing_type=mysql.DATETIME(),
               nullable=True,
               existing_server_default=sa.text('(now())'))
    op.alter_column('permission_abilities', 'created_at',
               existing_type=mysql.DATETIME(),
               nullable=True,
               existing_server_default=sa.text('(now())'))
    op.alter_column('permission_abilities', 'ability_key',
               existing_type=sa.String(length=50),
               type_=mysql.VARCHAR(length=30),
               existing_comment='能力键',
               existing_nullable=False)
    op.add_column('knowledge_group_relation', sa.Column('user_id', mysql.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key(op.f('knowledge_group_relation_ibfk_3'), 'knowledge_group_relation', 'user', ['user_id'], ['id'])
    op.create_index(op.f('uix_user_knowledge'), 'knowledge_group_relation', ['user_id', 'knowledge_id'], unique=True)
    op.drop_constraint(None, 'collect', type_='foreignkey')
    # ### end Alembic commands ###
