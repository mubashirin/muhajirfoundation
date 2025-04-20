from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from auth.dependencies import get_current_user
from users.models import User
from . import crud, schemas, models


router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Security(get_current_user)]
)


def get_admin_user(current_user: Annotated[User, Security(get_current_user)]):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions. Only admin can access this endpoint."
        )
    return current_user


@router.post("/admin", response_model=schemas.User)
def create_admin(
    user: schemas.UserCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Security(get_admin_user)]
):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_admin_user(db=db, user=user)


@router.post("/", response_model=schemas.User)
def create_user(
    user: schemas.UserCreate,
    db: Annotated[Session, Depends(get_db)]
):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@router.get("/", response_model=List[schemas.User])
def read_users(
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    skip: int = 0,
    limit: int = 100
):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/me", response_model=schemas.User)
def read_user_me(
    current_user: Annotated[models.User, Depends(get_current_user)]
):
    return current_user


@router.get("/{user_id}", response_model=schemas.User)
def read_user(
    user_id: int,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put("/{user_id}", response_model=schemas.User)
def update_user(
    user_id: int,
    user: schemas.UserUpdate,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_user = crud.update_user(db, user_id=user_id, user=user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.delete("/{user_id}", response_model=schemas.User)
def delete_user(
    user_id: int,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    db_user = crud.delete_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user 