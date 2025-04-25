from pydantic import BaseModel, UUID4
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class WalletBase(BaseModel):
    name: str
    usdt_trc20: Optional[str] = None
    bch: Optional[str] = None
    eth: Optional[str] = None
    btc: Optional[str] = None

class WalletCreate(WalletBase):
    pass

class WalletUpdate(WalletBase):
    pass

class Wallet(WalletBase):
    id: int
    uuid: UUID4
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class DonationCampaignBase(BaseModel):
    title: str
    description: str | None = None
    target_amount: Decimal
    wallet_id: int
    is_active: bool = True

class DonationCampaignCreate(DonationCampaignBase):
    pass

class DonationCampaignUpdate(DonationCampaignBase):
    pass

class DonationCampaign(DonationCampaignBase):
    id: int
    uuid: UUID4
    created_at: datetime
    updated_at: datetime
    wallet: Optional[Wallet] = None

    class Config:
        from_attributes = True 