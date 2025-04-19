from pydantic import BaseModel, Field, EmailStr
from typing import List


class FundInfo(BaseModel):
    id: int = Field(primary_key=True)
    address: str
    number: str
    email: EmailStr
    about_text: str
    social_links: List[str]