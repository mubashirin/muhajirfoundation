"""change id_telegram to bigint

Revision ID: 3c5883783d46
Revises: 0954cc89d6cf
Create Date: 2025-04-28 15:18:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3c5883783d46'
down_revision: Union[str, None] = '0954cc89d6cf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('tg_users', 'id_telegram',
               existing_type=sa.Integer(),
               type_=sa.BigInteger(),
               existing_nullable=False)


def downgrade() -> None:
    op.alter_column('tg_users', 'id_telegram',
               existing_type=sa.BigInteger(),
               type_=sa.Integer(),
               existing_nullable=False)
