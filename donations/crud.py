from sqlalchemy.orm import Session
from . import models, schemas
from typing import List, Optional

def create_campaign(db: Session, campaign: schemas.DonationCampaignCreate) -> models.DonationCampaign:
    db_campaign = models.DonationCampaign(**campaign.model_dump())
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign

def get_campaign(db: Session, campaign_id: int) -> Optional[models.DonationCampaign]:
    return db.query(models.DonationCampaign).filter(models.DonationCampaign.id == campaign_id).first()

def get_campaign_by_uuid(db: Session, uuid: str) -> Optional[models.DonationCampaign]:
    return db.query(models.DonationCampaign).filter(models.DonationCampaign.uuid == uuid).first()

def get_campaigns(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    active_only: bool = False
) -> List[models.DonationCampaign]:
    query = db.query(models.DonationCampaign)
    if active_only:
        query = query.filter(models.DonationCampaign.is_active == True)
    return query.offset(skip).limit(limit).all()

def update_campaign(
    db: Session, 
    campaign_id: int, 
    campaign: schemas.DonationCampaignUpdate
) -> Optional[models.DonationCampaign]:
    db_campaign = get_campaign(db, campaign_id)
    if not db_campaign:
        return None
    
    update_data = campaign.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_campaign, field, value)
    
    db.commit()
    db.refresh(db_campaign)
    return db_campaign

def delete_campaign(db: Session, campaign_id: int) -> bool:
    db_campaign = get_campaign(db, campaign_id)
    if not db_campaign:
        return False
    
    db.delete(db_campaign)
    db.commit()
    return True

def create_wallet(
    db: Session, 
    wallet: schemas.WalletCreate, 
    campaign_id: int
) -> Optional[models.Wallet]:
    db_wallet = models.Wallet(**wallet.model_dump(), campaign_id=campaign_id)
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