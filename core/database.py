from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.config import load_yaml_config

yaml_config = load_yaml_config()
db = yaml_config["database"]
db_url = f"{db['driver']}://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['name']}"

# Синхронное подключение (используется в большинстве кода)
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Синхронный генератор сессий
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 