import typer
from sqlalchemy.orm import Session
from core.config import get_settings, load_yaml_config
from core.database import get_db
from users.models import User
from core.security import get_password_hash
from alembic.config import Config
from alembic import command

app = typer.Typer()
settings = get_settings()

def create_admin(
    email: str,
    password: str,
    full_name: str = "Admin",
    db: Session = None
) -> None:
    """Создает администратора в БД"""
    if db is None:
        db = next(get_db())
    
    try:
        # Проверяем, существует ли уже админ
        admin = db.query(User).filter(User.email == email).first()
        if admin:
            typer.echo("Admin already exists!")
            return

        # Создаем админа
        admin = User(
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            is_active=True,
            is_superuser=True
        )
        db.add(admin)
        db.commit()
        typer.echo(f"Admin created successfully! Email: {email}")
    finally:
        if db is not None:
            db.close()

def run_migrations() -> None:
    """Применяет миграции к БД"""
    try:
        yaml_config = load_yaml_config()
        db = yaml_config["database"]
        db_url = f"{db['driver']}://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['name']}"
        
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", db_url)
        command.upgrade(alembic_cfg, "head")
        typer.echo("Migrations applied successfully!")
    except Exception as e:
        typer.echo(f"Error applying migrations: {str(e)}")
        raise typer.Exit(code=1)

@app.command()
def init(
    email: str = typer.Option(..., prompt=True, help="Admin email"),
    password: str = typer.Option(..., prompt=True, hide_input=True, confirmation_prompt=True, help="Admin password"),
    full_name: str = typer.Option("Admin", help="Admin full name")
) -> None:
    """Инициализирует проект: применяет миграции и создает администратора"""
    # Применяем миграции
    run_migrations()
    
    # Создаем админа
    create_admin(email, password, full_name)

if __name__ == "__main__":
    app() 