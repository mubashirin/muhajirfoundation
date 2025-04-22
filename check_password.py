from core.database import SessionLocal
from users.models import User

def check_password_format():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "gracioso@pm.me").first()
        if user:
            print(f"Hashed password: {user.hashed_password}")
            print(f"Length: {len(user.hashed_password)}")
            print(f"Format starts with: {user.hashed_password[:10]}...")
        else:
            print("User not found")
    finally:
        db.close()

if __name__ == "__main__":
    check_password_format()