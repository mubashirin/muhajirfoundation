from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class SocialLinkBase(BaseModel):
    platform: str
    url: str

class SocialLinkCreate(SocialLinkBase):
    fund_id: int

class SocialLink(SocialLinkBase):
    id: int
    fund_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class BankDetailBase(BaseModel):
    bank_name: str
    account_number: str
    swift_code: Optional[str] = None
    iban: Optional[str] = None
    currency: str

class BankDetailCreate(BankDetailBase):
    fund_id: int

class BankDetail(BankDetailBase):
    id: int
    fund_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class FundInfoBase(BaseModel):
    name: str
    description: str
    address: str
    phone: str
    email: EmailStr

class FundInfoCreate(FundInfoBase):
    pass

class FundInfoUpdate(FundInfoBase):
    is_active: Optional[bool] = None

class FundInfo(FundInfoBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    social_links: List[SocialLink] = []
    bank_details: List[BankDetail] = []

    class Config:
        from_attributes = True 