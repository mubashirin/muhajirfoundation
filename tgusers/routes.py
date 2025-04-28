from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from users.models import User
from tgusers.models import TgUsers
from tgusers.schemas import TgUserCreate, TgUserUpdate, TgUserOut
from admin.deps import get_current_admin
import uuid
from core.config import get_settings
import hmac
import hashlib
from core.security import verify_api_key

settings = get_settings()

router = APIRouter(prefix="/admin/tg", tags=["tg"])

def verify_telegram_hash(telegram_id: int, hash: str) -> bool:
    data_check_string = f"id={telegram_id}"
    secret_key = hashlib.sha256(settings.BOT_TOKEN.encode()).digest()
    hash_string = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()
    return hash == hash_string

@router.get("/users", response_model=List[TgUserOut])
def get_tgusers(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return db.query(TgUsers).all()

@router.post("/users", response_model=TgUserOut)
def create_tguser(user: TgUserCreate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    user_data = user.dict()
    user_data['uuid_id'] = str(uuid.uuid4())
    tguser = TgUsers(**user_data)
    db.add(tguser)
    db.commit()
    db.refresh(tguser)
    return tguser

@router.put("/users/{tguser_id}", response_model=TgUserOut)
def update_tguser(tguser_id: int, user: TgUserUpdate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    tguser = db.query(TgUsers).filter(TgUsers.id == tguser_id).first()
    if not tguser:
        raise HTTPException(status_code=404, detail="TgUser not found")
    for field, value in user.dict(exclude_unset=True).items():
        setattr(tguser, field, value)
    db.commit()
    db.refresh(tguser)
    return tguser

@router.delete("/users/{tguser_id}")
def delete_tguser(tguser_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    tguser = db.query(TgUsers).filter(TgUsers.id == tguser_id).first()
    if not tguser:
        raise HTTPException(status_code=404, detail="TgUser not found")
    db.delete(tguser)
    db.commit()
    return {"message": "TgUser deleted successfully"}

router = APIRouter(prefix="/api/v1", tags=["tg"])

@router.get("/tg/all")
def get_tg_ids(
    x_api_key: str = Header(..., alias="x-api-key"),
    x_api_signature: str = Header(..., alias="x-api-signature"),
    db: Session = Depends(get_db)
):
    # Формируем строку для подписи (можно просто 'all' для списка)
    data = "all"
    if not verify_api_key(db, x_api_key, x_api_signature, data):
        raise HTTPException(status_code=403, detail="Invalid API key or signature")
    tg_ids = db.query(TgUsers.id_telegram).all()
    return [tg_id for (tg_id,) in tg_ids] 