"""drop target_amount column from donation_campaigns

Revision ID: c4056afe6e02
Revises: 3c5883783d46
Create Date: 2025-05-02 14:55:39.827327

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c4056afe6e02'
down_revision: Union[str, None] = '3c5883783d46'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Удаляем только столбец target_amount
    op.drop_column('donation_campaigns', 'target_amount')


def downgrade() -> None:
    # Возвращаем столбец target_amount
    from sqlalchemy import Numeric
    op.add_column('donation_campaigns', sa.Column('target_amount', sa.Numeric(10, 2), nullable=False, server_default='0'))
