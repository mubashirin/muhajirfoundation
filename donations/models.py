from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, UUID, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime

from core.database import Base

class DonationCampaign(Base):
    __tablename__ = "donation_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    target_amount = Column(Numeric(10, 2), nullable=False, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    wallets = relationship("Wallet", back_populates="campaign", cascade="all, delete-orphan")

    def __str__(self):
        return self.title

class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    name = Column(String, nullable=False)
    campaign_id = Column(Integer, ForeignKey("donation_campaigns.id", ondelete="CASCADE"), nullable=False)
    usdt_trc20 = Column(String, nullable=True)
    bch = Column(String, nullable=True)
    eth = Column(String, nullable=True)
    btc = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    campaign = relationship("DonationCampaign", back_populates="wallets")

    def __str__(self):
        return f"{self.name} (ID: {self.id})"