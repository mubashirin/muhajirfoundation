"""merge heads

Revision ID: c756c8246f04
Revises: 34567fb2ae5e, df6e1b9d3596
Create Date: 2025-04-25 15:19:45.762936

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c756c8246f04'
down_revision: Union[str, None] = ('34567fb2ae5e', 'df6e1b9d3596')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
