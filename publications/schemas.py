from pydantic import BaseModel
from typing import Optional, List
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

class PublicationImage(BaseModel):
    id: int
    image: str
    class Config:
        from_attributes = True

class PublicationVideo(BaseModel):
    id: int
    video: str
    class Config:
        from_attributes = True

class Publication(PublicationBase):
    id: int
    views: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    images: List[PublicationImage] = []
    videos: List[PublicationVideo] = []

    class Config:
        from_attributes = True 