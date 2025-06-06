"""add publication images and videos

Revision ID: 286480d8b2fe
Revises: db80cabd3e5d
Create Date: 2025-04-27 21:31:26.048582

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '286480d8b2fe'
down_revision: Union[str, None] = 'db80cabd3e5d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### исправлено вручную: только добавление новых таблиц ###
    op.create_table(
        'publication_images',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('publication_id', sa.Integer(), sa.ForeignKey('publications.id', ondelete='CASCADE'), nullable=False),
        sa.Column('image', sa.String(), nullable=False),
    )
    op.create_index('ix_publication_images_id', 'publication_images', ['id'], unique=False)

    op.create_table(
        'publication_videos',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('publication_id', sa.Integer(), sa.ForeignKey('publications.id', ondelete='CASCADE'), nullable=False),
        sa.Column('video', sa.String(), nullable=False),
    )
    op.create_index('ix_publication_videos_id', 'publication_videos', ['id'], unique=False)


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_publications_id', table_name='publications')
    op.drop_table('publications')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_table('users')
    op.drop_index('ix_bank_details_id', table_name='bank_details')
    op.drop_table('bank_details')
    op.drop_index('ix_feedback_id', table_name='feedback')
    op.drop_table('feedback')
    op.drop_index('ix_publication_images_id', table_name='publication_images')
    op.drop_table('publication_images')
    op.drop_index('ix_fund_info_id', table_name='fund_info')
    op.drop_table('fund_info')
    op.drop_index('ix_social_links_id', table_name='social_links')
    op.drop_table('social_links')
    op.drop_index('ix_donations_id', table_name='donations')
    op.drop_index('ix_donations_uuid', table_name='donations')
    op.drop_table('donations')
    op.drop_index('ix_admins_email', table_name='admins')
    op.drop_index('ix_admins_id', table_name='admins')
    op.drop_index('ix_admins_username', table_name='admins')
    op.drop_table('admins')
    op.drop_index('ix_wallets_id', table_name='wallets')
    op.drop_index('ix_wallets_uuid', table_name='wallets')
    op.drop_table('wallets')
    op.drop_index('ix_publication_videos_id', table_name='publication_videos')
    op.drop_table('publication_videos')
    op.drop_index('ix_donation_campaigns_id', table_name='donation_campaigns')
    op.drop_index('ix_donation_campaigns_uuid', table_name='donation_campaigns')
    op.drop_table('donation_campaigns')
    # ### end Alembic commands ###
