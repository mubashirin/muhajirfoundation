from pydantic import BaseModel, EmailStr
from typing import List, Dict
from datetime import datetime

class SocialLinks(BaseModel):
    facebook: str | None = None
    instagram: str | None = None
    telegram: str | None = None
    youtube: str | None = None
    vk: str | None = None

class FundInfoBase(BaseModel):
    name: str
    description: str
    address: str
    phone: str
    email: EmailStr
    social_links: SocialLinks
    bank_details: Dict[str, str]

class FundInfoCreate(FundInfoBase):
    pass

class FundInfoUpdate(FundInfoBase):
    is_active: bool | None = None

class FundInfo(FundInfoBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True 