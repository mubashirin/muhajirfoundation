from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from users.models import User
from donations.models import DonationCampaign, Wallet
from donations.schemas import DonationCampaignCreate, DonationCampaignUpdate, DonationCampaignResponse, WalletCreate, WalletUpdate, WalletResponse
from admin.deps import get_current_admin
from admin.crud import BaseCRUD

router = APIRouter(prefix="/admin/donations", tags=["admin-donations"])

campaign_crud = BaseCRUD(DonationCampaign)
wallet_crud = BaseCRUD(Wallet)

# --- Campaigns ---
@router.get("/campaigns", response_model=List[DonationCampaignResponse])
async def get_campaigns(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    return campaign_crud.get_multi(db, skip=skip, limit=limit)

@router.get("/campaigns/{campaign_id}", response_model=DonationCampaignResponse)
async def get_campaign(campaign_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    campaign = campaign_crud.get(db, id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign

@router.post("/campaigns", response_model=DonationCampaignResponse)
async def create_campaign(campaign_in: DonationCampaignCreate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return campaign_crud.create(db, obj_in=campaign_in)

@router.put("/campaigns/{campaign_id}", response_model=DonationCampaignResponse)
async def update_campaign(campaign_id: int, campaign_in: DonationCampaignUpdate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    campaign = campaign_crud.get(db, id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign_crud.update(db, db_obj=campaign, obj_in=campaign_in)

@router.delete("/campaigns/{campaign_id}")
async def delete_campaign(campaign_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    campaign = campaign_crud.get(db, id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    campaign_crud.remove(db, id=campaign_id)
    return {"message": "Campaign deleted successfully"}

# --- Wallets ---
@router.get("/wallets", response_model=List[WalletResponse])
async def get_wallets(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    return wallet_crud.get_multi(db, skip=skip, limit=limit)

@router.get("/wallets/{wallet_id}", response_model=WalletResponse)
async def get_wallet(wallet_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    wallet = wallet_crud.get(db, id=wallet_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet

@router.post("/wallets", response_model=WalletResponse)
async def create_wallet(wallet_in: WalletCreate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return wallet_crud.create(db, obj_in=wallet_in)

@router.put("/wallets/{wallet_id}", response_model=WalletResponse)
async def update_wallet(wallet_id: int, wallet_in: WalletUpdate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    wallet = wallet_crud.get(db, id=wallet_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet_crud.update(db, db_obj=wallet, obj_in=wallet_in)

@router.delete("/wallets/{wallet_id}")
async def delete_wallet(wallet_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    wallet = wallet_crud.get(db, id=wallet_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    wallet_crud.remove(db, id=wallet_id)
    return {"message": "Wallet deleted successfully"} 