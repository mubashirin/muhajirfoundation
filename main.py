from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from pathlib import Path

from core.config import get_settings
from core.database import engine, Base
from admin import setup_admin
from users.routes import router as users_router
from auth import router as auth_router
from fund import router as fund_router

settings = get_settings()

# Настройка логирования
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format=settings.LOG_FORMAT,
    filename=settings.LOG_FILE
)

# Создаем таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

# Подключаем админку
admin = setup_admin(app, engine)

# Подключение роутеров
app.include_router(users_router, prefix=settings.API_V1_STR)
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(fund_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Welcome to Muhajir Foundation API"} 