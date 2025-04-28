from sqlalchemy.orm import Session
from core.models import ApiKey
from schemas.api_key import APIKeyCreate, APIKeyUpdate
import secrets
import string


def generate_api_key() -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(32))


def generate_api_secret() -> str:
    return secrets.token_urlsafe(32)


def create_api_key(db: Session, api_key: APIKeyCreate) -> ApiKey:
    db_api_key = ApiKey(
        name=api_key.name,
        api_key=generate_api_key(),
        api_secret=generate_api_secret(),
        is_active=api_key.is_active
    )
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    return db_api_key


def get_api_key(db: Session, api_key_id: int) -> ApiKey:
    return db.query(ApiKey).filter(ApiKey.id == api_key_id).first()


def get_api_key_by_key(db: Session, api_key: str) -> ApiKey:
    return db.query(ApiKey).filter(ApiKey.api_key == api_key).first()


def get_api_keys(db: Session, skip: int = 0, limit: int = 100) -> list[ApiKey]:
    return db.query(ApiKey).offset(skip).limit(limit).all()


def update_api_key(db: Session, api_key_id: int, api_key: APIKeyUpdate) -> ApiKey:
    db_api_key = get_api_key(db, api_key_id)
    if db_api_key:
        for key, value in api_key.dict(exclude_unset=True).items():
            setattr(db_api_key, key, value)
        db.commit()
        db.refresh(db_api_key)
    return db_api_key


def delete_api_key(db: Session, api_key_id: int) -> bool:
    db_api_key = get_api_key(db, api_key_id)
    if db_api_key:
        db.delete(db_api_key)
        db.commit()
        return True
    return False 