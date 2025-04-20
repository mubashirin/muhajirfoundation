"""add_relationships_between_fund_info_and_social_links

Revision ID: 1e5a53a495bf
Revises: 4edc533b3654
Create Date: 2025-04-20 13:17:08.212197

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1e5a53a495bf'
down_revision: Union[str, None] = '4edc533b3654'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем комментарии к таблицам и колонкам
    op.execute("COMMENT ON TABLE fund_info IS 'Основная информация о фонде'")
    op.execute("COMMENT ON TABLE social_links IS 'Социальные ссылки фонда'")
    
    op.execute("COMMENT ON COLUMN fund_info.id IS 'Уникальный идентификатор фонда'")
    op.execute("COMMENT ON COLUMN fund_info.name IS 'Название фонда'")
    op.execute("COMMENT ON COLUMN fund_info.description IS 'Описание фонда'")
    op.execute("COMMENT ON COLUMN fund_info.address IS 'Адрес фонда'")
    op.execute("COMMENT ON COLUMN fund_info.phone IS 'Контактный телефон'")
    op.execute("COMMENT ON COLUMN fund_info.email IS 'Контактный email'")
    op.execute("COMMENT ON COLUMN fund_info.is_active IS 'Статус активности фонда'")
    
    op.execute("COMMENT ON COLUMN social_links.id IS 'Уникальный идентификатор социальной ссылки'")
    op.execute("COMMENT ON COLUMN social_links.fund_id IS 'ID фонда, которому принадлежит ссылка'")
    op.execute("COMMENT ON COLUMN social_links.platform IS 'Название социальной платформы (instagram, facebook и т.д.)'")
    op.execute("COMMENT ON COLUMN social_links.url IS 'URL социальной ссылки'")
    op.execute("COMMENT ON COLUMN social_links.created_at IS 'Дата создания записи'")
    op.execute("COMMENT ON COLUMN social_links.updated_at IS 'Дата последнего обновления записи'")


def downgrade() -> None:
    # Удаляем комментарии
    op.execute("COMMENT ON TABLE fund_info IS NULL")
    op.execute("COMMENT ON TABLE social_links IS NULL")
    
    op.execute("COMMENT ON COLUMN fund_info.id IS NULL")
    op.execute("COMMENT ON COLUMN fund_info.name IS NULL")
    op.execute("COMMENT ON COLUMN fund_info.description IS NULL")
    op.execute("COMMENT ON COLUMN fund_info.address IS NULL")
    op.execute("COMMENT ON COLUMN fund_info.phone IS NULL")
    op.execute("COMMENT ON COLUMN fund_info.email IS NULL")
    op.execute("COMMENT ON COLUMN fund_info.is_active IS NULL")
    
    op.execute("COMMENT ON COLUMN social_links.id IS NULL")
    op.execute("COMMENT ON COLUMN social_links.fund_id IS NULL")
    op.execute("COMMENT ON COLUMN social_links.platform IS NULL")
    op.execute("COMMENT ON COLUMN social_links.url IS NULL")
    op.execute("COMMENT ON COLUMN social_links.created_at IS NULL")
    op.execute("COMMENT ON COLUMN social_links.updated_at IS NULL")
