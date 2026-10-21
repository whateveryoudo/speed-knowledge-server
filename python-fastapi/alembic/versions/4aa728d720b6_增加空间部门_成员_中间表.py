"""增加空间部门,成员,中间表

Revision ID: 4aa728d720b6
Revises: cd719dbf683b
Create Date: 2026-10-20 18:59:00.000000

"""
from typing import Sequence, Union
import uuid
from datetime import datetime
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '4aa728d720b6'
down_revision: Union[str, None] = 'cd719dbf683b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()

    # 1. 创建空间部门表 (space_department)
    if 'space_department' not in existing_tables:
        op.create_table(
            'space_department',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('space_id', sa.String(length=36), nullable=False, comment='所属空间ID'),
            sa.Column('parent_id', sa.String(length=36), nullable=True, comment='父部门ID(NULL为根部门)'),
            sa.Column('name', sa.String(length=100), nullable=False, comment='部门名称'),
            sa.Column('sort_order', sa.Integer(), nullable=False, server_default=sa.text('0'), comment='排序'),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp(), comment='创建时间'),
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp(), comment='更新时间'),
            sa.ForeignKeyConstraint(['parent_id'], ['space_department.id'], ondelete='SET NULL'),
            sa.ForeignKeyConstraint(['space_id'], ['space.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_space_department_parent_id'), 'space_department', ['parent_id'], unique=False)
        op.create_index(op.f('ix_space_department_space_id'), 'space_department', ['space_id'], unique=False)

    # 2. 创建成员-部门关联中间表 (space_department_member)
    if 'space_department_member' not in existing_tables:
        op.create_table(
            'space_department_member',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('department_id', sa.String(length=36), nullable=False, comment='部门ID'),
            sa.Column('space_member_id', sa.String(length=36), nullable=False, comment='空间成员ID'),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp(), comment='创建时间'),
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp(), comment='更新时间'),
            sa.ForeignKeyConstraint(['department_id'], ['space_department.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['space_member_id'], ['space_member.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('department_id', 'space_member_id', name='uq_dept_space_member')
        )
        op.create_index(op.f('ix_space_department_member_department_id'), 'space_department_member', ['department_id'], unique=False)
        op.create_index(op.f('ix_space_department_member_space_member_id'), 'space_department_member', ['space_member_id'], unique=False)

    # 3. 解除 team_member 上的老外键和老字段（安全解绑）
    try:
        op.drop_constraint(op.f('team_member_ibfk_1'), 'team_member', type_='foreignkey')
    except Exception:
        pass
    try:
        op.drop_column('team_member', 'dept_id')
    except Exception:
        pass

    # 4. 删除老表 space_dept
    if 'space_dept' in existing_tables:
        op.drop_table('space_dept')

    # 5. 成员表追加软删除字段 deleted_at
    member_cols = [c['name'] for c in inspector.get_columns('space_member')]
    if 'deleted_at' not in member_cols:
        op.add_column('space_member', sa.Column('deleted_at', sa.DateTime(), nullable=True, comment='删除时间(NULL表示未删除)'))

    # 6. --- 存量数据回填 (Data Migration) ---
    spaces = bind.execute(sa.text("SELECT id, name FROM space WHERE type = 'organization'")).fetchall()
    now = datetime.now()
    for space in spaces:
        space_id, space_name = space[0], space[1]
        
        # 查找或生成根部门
        root_dept = bind.execute(
            sa.text("SELECT id FROM space_department WHERE space_id = :sid AND parent_id IS NULL LIMIT 1"),
            {"sid": space_id}
        ).fetchone()

        if root_dept:
            root_dept_id = root_dept[0]
        else:
            root_dept_id = str(uuid.uuid4())
            bind.execute(
                sa.text(
                    "INSERT INTO space_department (id, space_id, parent_id, name, sort_order, created_at, updated_at) "
                    "VALUES (:id, :sid, NULL, :name, 0, :now, :now)"
                ),
                {"id": root_dept_id, "sid": space_id, "name": space_name or "默认部门", "now": now}
            )

        # 查找该空间下在职、且未绑定任何部门的成员，全部绑定到根部门
        members = bind.execute(
            sa.text(
                "SELECT sm.id FROM space_member sm "
                "WHERE sm.space_id = :sid AND sm.deleted_at IS NULL "
                "AND NOT EXISTS (SELECT 1 FROM space_department_member sdm WHERE sdm.space_member_id = sm.id)"
            ),
            {"sid": space_id}
        ).fetchall()

        for m in members:
            bind.execute(
                sa.text(
                    "INSERT INTO space_department_member (id, department_id, space_member_id, created_at, updated_at) "
                    "VALUES (:id, :dept_id, :mid, :now, :now)"
                ),
                {"id": str(uuid.uuid4()), "dept_id": root_dept_id, "mid": m[0], "now": now}
            )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()

    # 1. 移除 soft delete 列
    member_cols = [c['name'] for c in inspector.get_columns('space_member')]
    if 'deleted_at' in member_cols:
        op.drop_column('space_member', 'deleted_at')

    # 2. 移除中间表
    if 'space_department_member' in existing_tables:
        op.drop_index(op.f('ix_space_department_member_space_member_id'), table_name='space_department_member')
        op.drop_index(op.f('ix_space_department_member_department_id'), table_name='space_department_member')
        op.drop_table('space_department_member')

    # 3. 移除部门表
    if 'space_department' in existing_tables:
        op.drop_index(op.f('ix_space_department_space_id'), table_name='space_department')
        op.drop_index(op.f('ix_space_department_parent_id'), table_name='space_department')
        op.drop_table('space_department')

    # 4. 恢复老表 space_dept
    if 'space_dept' not in existing_tables:
        op.create_table(
            'space_dept',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('space_id', sa.String(length=36), nullable=False, comment='所属空间ID'),
            sa.Column('name', sa.String(length=30), nullable=False, comment='部门名称'),
            sa.Column('order', sa.Integer(), nullable=False, comment='排序'),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.current_timestamp(), nullable=False, comment='创建时间'),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.func.current_timestamp(), nullable=False, comment='更新时间'),
            sa.Column('deleted_at', sa.DateTime(), nullable=True, comment='删除时间(NULL表示未删除)'),
            sa.ForeignKeyConstraint(['space_id'], ['space.id'], name='space_dept_ibfk_1'),
            sa.PrimaryKeyConstraint('id')
        )

    # 5. 恢复 team_member.dept_id 及外键
    team_cols = [c['name'] for c in inspector.get_columns('team_member')]
    if 'dept_id' not in team_cols:
        op.add_column('team_member', sa.Column('dept_id', sa.String(length=36), nullable=True, comment='部门ID'))
        op.create_foreign_key(op.f('team_member_ibfk_1'), 'team_member', 'space_dept', ['dept_id'], ['id'], ondelete='CASCADE')
