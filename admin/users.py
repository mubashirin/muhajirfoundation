from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from users.models import User
from users.schemas import UserCreate, UserUpdate, UserResponse
from admin.deps import get_current_admin
from admin.crud import BaseCRUD
from core.security import get_password_hash

router = APIRouter(prefix="/admin/users", tags=["admin-users"])

user_crud = BaseCRUD(User)

@router.get("/", response_model=List[UserResponse])
async def get_users(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    return user_crud.get_multi(db, skip=skip, limit=limit)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=UserResponse)
async def create_user(
    user_in: UserCreate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user_in.password)
    user_data = user_in.model_dump(exclude={"password"})
    user_data["hashed_password"] = hashed_password
    
    return user_crud.create(db, obj_in=user_data)

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_in.password:
        user_in.hashed_password = get_password_hash(user_in.password)
        user_in = user_in.model_dump(exclude={"password"})
    
    return user_crud.update(db, db_obj=user, obj_in=user_in)

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_crud.remove(db, id=user_id)
    return {"message": "User deleted successfully"} 