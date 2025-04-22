from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from pathlib import Path
from core.config import get_settings
from core.database import engine, Base
from users.routes import router as users_router
from fund.routes import router as fund_router
from feedback.routes import router as feedback_router
from donations.routes import router as donations_router
from admin import init_admin_routes

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
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(users_router, prefix=settings.API_V1_STR)
app.include_router(fund_router, prefix=settings.API_V1_STR)
app.include_router(feedback_router, prefix=settings.API_V1_STR)
app.include_router(donations_router, prefix=settings.API_V1_STR)

# Инициализация админ-роутов
init_admin_routes(app)

@app.get("/")
async def root():
    return {"message": "Welcome to Muhajir Foundation API"} 