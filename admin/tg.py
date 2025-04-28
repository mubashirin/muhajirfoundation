from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from users.models import User
from tgusers.models import TgUsers
from tgusers.schemas import TgUserCreate, TgUserUpdate, TgUserOut
from admin.deps import get_current_admin
import uuid

router = APIRouter(prefix="/admin/tg", tags=["admin"])

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