"""add file_path to publication

Revision ID: fcf225a20d78
Revises: c756c8246f04
Create Date: 2025-04-26 13:58:05.156649

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'fcf225a20d78'
down_revision: Union[str, None] = 'c756c8246f04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('publications', sa.Column('file_path', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('publications', 'file_path')
