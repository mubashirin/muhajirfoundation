from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, UUID, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime

from core.database import Base

class DonationCampaign(Base):
    __tablename__ = "donation_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    wallet = relationship("Wallet")

    def __str__(self):
        return self.title

class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    usdt_trc20 = Column(String, nullable=True)
    bch = Column(String, nullable=True)
    eth = Column(String, nullable=True)
    btc = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    def __str__(self):
        return f"{self.name} (ID: {self.id})"