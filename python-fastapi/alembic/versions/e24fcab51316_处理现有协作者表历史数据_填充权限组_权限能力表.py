"""处理现有协作者表历史数据,填充权限组,权限能力表

Revision ID: e24fcab51316
Revises: cf85bfd43b0e
Create Date: 2026-02-05 19:03:48.900859

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e24fcab51316'
down_revision: Union[str, None] = 'cf85bfd43b0e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
