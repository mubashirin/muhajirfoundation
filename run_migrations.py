import os
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в PYTHONPATH
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Импортируем и запускаем Alembic
from alembic.config import Config
from alembic import command

alembic_cfg = Config("alembic.ini")
command.upgrade(alembic_cfg, "head") 