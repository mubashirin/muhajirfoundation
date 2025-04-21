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

@router.post("/campaigns", response_model=schemas.DonationCampaign)
def create_campaign(
    campaign: schemas.DonationCampaignCreate,
    db: Session = Depends(get_db)
):
    """Создать новую кампанию по сбору средств"""
    return crud.create_campaign(db, campaign)

@router.put("/campaigns/{campaign_id}", response_model=schemas.DonationCampaign)
def update_campaign(
    campaign_id: int,
    campaign: schemas.DonationCampaignUpdate,
    db: Session = Depends(get_db)
):
    """Обновить информацию о кампании"""
    updated_campaign = crud.update_campaign(db, campaign_id, campaign)
    if not updated_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return updated_campaign

@router.delete("/campaigns/{campaign_id}")
def delete_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Удалить кампанию"""
    if not crud.delete_campaign(db, campaign_id):
        raise HTTPException(status_code=404, detail="Campaign not found")
    return {"message": "Campaign deleted successfully"}

# Роуты для кошельков
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

@router.post("/wallets", response_model=schemas.Wallet)
def create_wallet(
    wallet: schemas.WalletCreate,
    db: Session = Depends(get_db)
):
    """Создать новый кошелек"""
    return crud.create_wallet(db, wallet)

@router.put("/wallets/{wallet_id}", response_model=schemas.Wallet)
def update_wallet(
    wallet_id: int,
    wallet: schemas.WalletUpdate,
    db: Session = Depends(get_db)
):
    """Обновить информацию о кошельке"""
    updated_wallet = crud.update_wallet(db, wallet_id, wallet)
    if not updated_wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return updated_wallet

@router.delete("/wallets/{wallet_id}")
def delete_wallet(wallet_id: int, db: Session = Depends(get_db)):
    """Удалить кошелек"""
    if not crud.delete_wallet(db, wallet_id):
        raise HTTPException(status_code=404, detail="Wallet not found")
    return {"message": "Wallet deleted successfully"} 