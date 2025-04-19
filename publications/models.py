from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Publication(BaseModel):
    id: int = Field(primary_key=True)
    title: str
    slug: str
    create_at: datetime
    update_at: datetime
    photo: str
    text: str
    is_active: bool
    is_fundraising: bool
    views: int
    source_link: Optional[str] = None