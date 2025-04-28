from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class APIKeyBase(BaseModel):
    name: str = Field(..., max_length=100)
    is_active: bool = Field(default=True)


class APIKeyCreate(APIKeyBase):
    pass


class APIKeyUpdate(APIKeyBase):
    name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


class APIKeyInDB(APIKeyBase):
    id: int
    api_key: str
    api_secret: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class APIKeyResponse(APIKeyBase):
    id: int
    api_key: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 