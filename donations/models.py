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
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    wallets = relationship("Wallet", back_populates="campaign", cascade="all, delete-orphan")
    donations = relationship("Donation", back_populates="campaign")

    def __str__(self):
        return self.title

class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    name = Column(String, nullable=False)
    campaign_id = Column(Integer, ForeignKey("donation_campaigns.id", ondelete="SET NULL"), nullable=True)
    usdt_trc20 = Column(String, nullable=True)
    bch = Column(String, nullable=True)
    eth = Column(String, nullable=True)
    btc = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    campaign = relationship("DonationCampaign", back_populates="wallets")

    def __str__(self):
        return f"{self.name} (ID: {self.id})"

class Donation(Base):
    __tablename__ = "donations"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    campaign_id = Column(Integer, ForeignKey("donation_campaigns.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String, nullable=False)
    donor_name = Column(String, nullable=True)
    donor_email = Column(String, nullable=True)
    donor_phone = Column(String, nullable=True)
    message = Column(Text, nullable=True)
    is_anonymous = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    campaign = relationship("DonationCampaign", back_populates="donations")

    def __str__(self):
        return f"Donation {self.id} - {self.amount} {self.currency}"