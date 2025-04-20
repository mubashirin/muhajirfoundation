from core.database import SessionLocal
from admin import Admin
from core.security import get_password_hash

def create_admin():
    db = SessionLocal()
    try:
        admin = Admin(
            username="admin",
            password=get_password_hash("admin123"),
            is_superuser=True
        )
        db.add(admin)
        db.commit()
        print("Admin created successfully!")
    except Exception as e:
        print(f"Error creating admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin() 