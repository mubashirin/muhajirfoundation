from core.database import get_db
from users.models import User
from fund.models import FundInfo

def check_database():
    db = next(get_db())
    
    # Проверяем пользователей
    users = db.query(User).all()
    print("\nUsers in database:")
    for user in users:
        print(f"ID: {user.id}, Email: {user.email}, Is Superuser: {user.is_superuser}")
        # Делаем пользователя администратором
        if user.email == "gracioso@pm.me":
            user.is_superuser = True
            db.commit()
            print(f"User {user.email} is now an admin")
    
    # Проверяем информацию о фонде
    try:
        fund_info = db.query(FundInfo).first()
        print("\nFund info in database:")
        if fund_info:
            print(f"ID: {fund_info.id}, Name: {fund_info.name}")
        else:
            print("No fund info found")
    except Exception as e:
        print(f"\nError checking fund info: {e}")

if __name__ == "__main__":
    check_database() 