from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from donations import schemas, crud

router = APIRouter(tags=["donations"])

@router.get("/campaigns", response_model=List[schemas.DonationCampaign])
def get_campaigns(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получить список кампаний по сбору средств"""
    return crud.get_campaigns(db, skip=skip, limit=limit)

@router.get("/campaigns/{campaign_id}", response_model=schemas.DonationCampaign)
def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Получить информацию о конкретной кампании"""
    campaign = crud.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign

@router.get("/wallets", response_model=List[schemas.Wallet])
def get_wallets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получить список кошельков"""
    return crud.get_wallets(db, skip=skip, limit=limit)

@router.get("/wallets/{wallet_id}", response_model=schemas.Wallet)
def get_wallet(wallet_id: int, db: Session = Depends(get_db)):
    """Получить информацию о конкретном кошельке"""
    wallet = crud.get_wallet(db, wallet_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet