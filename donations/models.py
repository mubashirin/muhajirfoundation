from pydantic import BaseModel
from datetime import datetime


class Wallet(BaseModel):
    id: int
    currency: str  # TRC20, BTC, ETH, TRON, BCH
    address: str
    publication_id: int = ForeignKey('publication.id')
    is_active: bool