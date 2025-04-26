"""add ipfs_link to publication

Revision ID: db80cabd3e5d
Revises: fcf225a20d78
Create Date: 2025-04-26 15:25:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'db80cabd3e5d'
down_revision: Union[str, None] = 'fcf225a20d78'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('publications', sa.Column('ipfs_link', sa.String(), nullable=True))

def downgrade() -> None:
    op.drop_column('publications', 'ipfs_link')
