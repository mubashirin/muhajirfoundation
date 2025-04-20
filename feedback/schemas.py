from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class FeedbackBase(BaseModel):
    name: str
    email: EmailStr
    message: str

class FeedbackCreate(FeedbackBase):
    pass

class FeedbackUpdate(BaseModel):
    is_read: Optional[bool] = None

class Feedback(FeedbackBase):
    id: int
    is_read: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
