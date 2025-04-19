# Muhajir Foundation API

FastAPI-based backend для Muhajir Foundation.

## Установка

1. Создайте виртуальное окружение:
```bash
python -m venv .venv
source .venv/bin/activate  # для Linux/Mac
# или
.venv\Scripts\activate  # для Windows
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Настройте переменные окружения:
```bash
cp .env.example .env
# Отредактируйте .env под ваши настройки
```

4. Запустите сервер:
```bash
uvicorn main:app --reload
```

## Структура проекта

- `auth/` - Аутентификация и авторизация
- `core/` - Основные настройки и утилиты
- `donations/` - Модуль пожертвований
- `fund/` - Модуль фонда
- `publications/` - Модуль публикаций
- `users/` - Модуль пользователей
- `common/` - Общие компоненты

## API Документация

После запуска сервера:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Разработка

- Используйте pre-commit хуки для проверки кода
- Следуйте PEP 8
- Пишите тесты для нового функционала
