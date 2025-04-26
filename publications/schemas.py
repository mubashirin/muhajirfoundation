from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PublicationBase(BaseModel):
    title: str
    slug: str
    photo: Optional[str] = None
    text: str
    is_active: bool = True
    is_fundraising: bool = False
    source_link: Optional[str] = None
    file_path: Optional[str] = None
    ipfs_link: Optional[str] = None

class PublicationCreate(PublicationBase):
    pass

class PublicationUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    photo: Optional[str] = None
    text: Optional[str] = None
    is_active: Optional[bool] = None
    is_fundraising: Optional[bool] = None
    source_link: Optional[str] = None
    file_path: Optional[str] = None
    ipfs_link: Optional[str] = None

class Publication(PublicationBase):
    id: int
    views: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 