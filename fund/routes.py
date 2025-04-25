from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from . import crud, schemas

router = APIRouter(prefix="/fund", tags=["fund"])

@router.get("/info", response_model=schemas.FundInfo)
def read_fund_info(
    db: Annotated[Session, Depends(get_db)]
):
    """Получить информацию о фонде"""
    fund_info = crud.get_fund_info(db)
    if not fund_info:
        raise HTTPException(status_code=404, detail="Fund info not found")
    return fund_info

@router.get("/social-links/{fund_id}", response_model=List[schemas.SocialLink])
def read_social_links(
    fund_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    """Получить социальные ссылки фонда"""
    return crud.get_social_links(db=db, fund_id=fund_id)

@router.get("/bank-details/{fund_id}", response_model=List[schemas.BankDetail])
def read_bank_details(
    fund_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    """Получить банковские реквизиты фонда"""
    return crud.get_bank_details(db=db, fund_id=fund_id) 