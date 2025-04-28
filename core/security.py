from datetime import datetime, timedelta
from typing import Any, Union, Optional

from jose import jwt
from passlib.context import CryptContext
import secrets
import string
import hmac
import hashlib
from sqlalchemy.orm import Session
from core.models import ApiKey

from core.config import get_settings

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta | None = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def generate_api_key() -> str:
    """Генерирует случайный API ключ"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(32))

def generate_api_secret() -> str:
    """Генерирует случайный API секрет"""
    return secrets.token_urlsafe(32)

def create_api_key(db: Session, name: str) -> ApiKey:
    """Создает новую пару API ключей"""
    api_key = ApiKey(
        api_key=generate_api_key(),
        api_secret=generate_api_secret(),
        name=name
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    return api_key

def verify_api_key(db: Session, api_key: str, signature: str, data: str) -> bool:
    """Проверяет подпись API запроса"""
    key = db.query(ApiKey).filter(
        ApiKey.api_key == api_key,
        ApiKey.is_active == True
    ).first()
    
    if not key:
        return False
        
    expected_signature = hmac.new(
        key.api_secret.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

def get_api_key_signature(api_secret: str, data: str) -> str:
    """Генерирует подпись для API запроса"""
    return hmac.new(
        api_secret.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()
