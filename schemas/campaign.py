from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class CampaignBase(BaseModel):
    title: str
    description: str
    wallet_id: int
    is_active: bool = True

class CampaignCreate(CampaignBase):
    pass

class CampaignUpdate(CampaignBase):
    pass

class Campaign(CampaignBase):
    id: int
    uuid: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 