from sqlalchemy.orm import Session
from core.database import SessionLocal, engine, Base
from users.models import User
from core.security import get_password_hash

def create_admin(email: str, password: str):
    db = SessionLocal()
    try:
        # Проверяем существует ли уже админ
        admin = db.query(User).filter(User.email == email).first()
        if admin:
            # Если админ существует, обновляем его пароль
            admin.hashed_password = get_password_hash(password)
            admin.is_superuser = True
            admin.is_active = True
            db.commit()
            print(f"Admin {email} password updated successfully")
        else:
            # Создаем нового админа
            admin = User(
                email=email,
                hashed_password=get_password_hash(password),
                is_superuser=True,
                is_active=True
            )
            db.add(admin)
            db.commit()
            print(f"Admin {email} created successfully")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Создаем таблицы если их нет
    Base.metadata.create_all(bind=engine)
    
    # Запрашиваем данные для админа
    email = input("Enter admin email: ")
    password = input("Enter admin password: ")
    
    # Создаем админа
    create_admin(email, password) 