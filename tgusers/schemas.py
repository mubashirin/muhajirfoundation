from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TgUserBase(BaseModel):
    id_telegram: int
    name: str

class TgUserCreate(TgUserBase):
    pass

class TgUserUpdate(BaseModel):
    name: Optional[str] = None

class TgUserOut(TgUserBase):
    id: int
    uuid_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True 