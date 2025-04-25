from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.config import get_settings

settings = get_settings()

# Синхронное подключение (используется в большинстве кода)
engine = create_engine(settings.get_database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Синхронный генератор сессий
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 