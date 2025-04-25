from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import async_sessionmaker

from core.config import get_settings

settings = get_settings()

# Синхронное подключение
engine = create_async_engine(
    settings.get_database_url.replace('postgresql://', 'postgresql+asyncpg://'),
    echo=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Асинхронное подключение
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

# Синхронный генератор сессий
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Асинхронный генератор сессий
async def get_async_db():
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close() 