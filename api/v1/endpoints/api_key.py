from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from crud.api_key import (
    create_api_key,
    get_api_key,
    get_api_keys,
    update_api_key,
    delete_api_key
)
from schemas.api_key import APIKeyCreate, APIKeyUpdate, APIKeyResponse
from admin.deps import get_current_admin

router = APIRouter(prefix="/admin/api-keys", tags=["admin"])


@router.post("/", response_model=APIKeyResponse)
def create_new_api_key(
    *,
    db: Session = Depends(get_db),
    api_key_in: APIKeyCreate,
    current_admin: dict = Depends(get_current_admin)
):
    api_key = create_api_key(db=db, api_key=api_key_in)
    return api_key


@router.get("/", response_model=List[APIKeyResponse])
def read_api_keys(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_admin: dict = Depends(get_current_admin)
):
    api_keys = get_api_keys(db, skip=skip, limit=limit)
    return api_keys


@router.get("/{api_key_id}", response_model=APIKeyResponse)
def read_api_key(
    api_key_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    api_key = get_api_key(db, api_key_id=api_key_id)
    if not api_key:
        raise HTTPException(
            status_code=404,
            detail="API key not found"
        )
    return api_key


@router.put("/{api_key_id}", response_model=APIKeyResponse)
def update_existing_api_key(
    api_key_id: int,
    *,
    db: Session = Depends(get_db),
    api_key_in: APIKeyUpdate,
    current_admin: dict = Depends(get_current_admin)
):
    api_key = get_api_key(db, api_key_id=api_key_id)
    if not api_key:
        raise HTTPException(
            status_code=404,
            detail="API key not found"
        )
    api_key = update_api_key(db=db, api_key_id=api_key_id, api_key=api_key_in)
    return api_key


@router.delete("/{api_key_id}")
def delete_existing_api_key(
    api_key_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    api_key = get_api_key(db, api_key_id=api_key_id)
    if not api_key:
        raise HTTPException(
            status_code=404,
            detail="API key not found"
        )
    delete_api_key(db=db, api_key_id=api_key_id)
    return {"msg": "API key successfully deleted"} 