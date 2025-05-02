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
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: bool = True

class FundInfoCreate(FundInfoBase):
    pass

class FundInfoUpdate(FundInfoBase):
    pass

class FundInfoResponse(FundInfoBase):
    id: int

    class Config:
        from_attributes = True

class FundInfo(FundInfoBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    social_links: List[SocialLink] = []
    bank_details: List[BankDetail] = []

    class Config:
        from_attributes = True 