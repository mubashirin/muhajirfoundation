from sqlalchemy.orm import Session
from . import models, schemas
from typing import List, Optional
from fastapi import HTTPException
from datetime import datetime

def create_donation_campaign(db: Session, campaign: schemas.DonationCampaignCreate) -> models.DonationCampaign:
    db_campaign = models.DonationCampaign(
        title=campaign.title,
        description=campaign.description,
        status=campaign.status,
        is_active=campaign.is_active
    )
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign

def get_donation_campaign(db: Session, campaign_id: int) -> models.DonationCampaign | None:
    return db.query(models.DonationCampaign).filter(models.DonationCampaign.id == campaign_id).first()

def get_campaign_by_uuid(db: Session, uuid: str) -> Optional[models.DonationCampaign]:
    return db.query(models.DonationCampaign).filter(models.DonationCampaign.uuid == uuid).first()

def get_donation_campaigns(db: Session, skip: int = 0, limit: int = 100) -> list[models.DonationCampaign]:
    return db.query(models.DonationCampaign).offset(skip).limit(limit).all()

def update_donation_campaign(
    db: Session, 
    campaign_id: int, 
    campaign_update: schemas.DonationCampaignUpdate
) -> models.DonationCampaign:
    db_campaign = get_donation_campaign(db, campaign_id)
    if not db_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    update_data = campaign_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_campaign, field, value)
    
    db.commit()
    db.refresh(db_campaign)
    return db_campaign

def delete_donation_campaign(db: Session, campaign_id: int) -> bool:
    db_campaign = get_donation_campaign(db, campaign_id)
    if not db_campaign:
        return False
    
    db.delete(db_campaign)
    db.commit()
    return True

def create_wallet(
    db: Session, 
    wallet: schemas.WalletCreate
) -> Optional[models.Wallet]:
    db_wallet = models.Wallet(**wallet.model_dump())
    db.add(db_wallet)
    db.commit()
    db.refresh(db_wallet)
    return db_wallet

def get_wallet(db: Session, wallet_id: int) -> Optional[models.Wallet]:
    return db.query(models.Wallet).filter(models.Wallet.id == wallet_id).first()

def get_wallet_by_uuid(db: Session, uuid: str) -> Optional[models.Wallet]:
    return db.query(models.Wallet).filter(models.Wallet.uuid == uuid).first()

def get_campaign_wallets(
    db: Session, 
    campaign_id: int,
    skip: int = 0, 
    limit: int = 100
) -> List[models.Wallet]:
    return db.query(models.Wallet).filter(
        models.Wallet.campaign_id == campaign_id
    ).offset(skip).limit(limit).all()

def update_wallet(
    db: Session, 
    wallet_id: int, 
    wallet: schemas.WalletUpdate
) -> Optional[models.Wallet]:
    db_wallet = get_wallet(db, wallet_id)
    if not db_wallet:
        return None
    
    update_data = wallet.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_wallet, field, value)
    
    db.commit()
    db.refresh(db_wallet)
    return db_wallet

def delete_wallet(db: Session, wallet_id: int) -> bool:
    db_wallet = get_wallet(db, wallet_id)
    if not db_wallet:
        return False
    
    db.delete(db_wallet)
    db.commit()
    return True

def get_wallets(
    db: Session, 
    skip: int = 0, 
    limit: int = 100
) -> List[models.Wallet]:
    return db.query(models.Wallet).offset(skip).limit(limit).all() 