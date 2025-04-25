from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, UUID, ForeignKey
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

class DonationCampaign(Base):
    __tablename__ = "donation_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    wallet = relationship("Wallet", back_populates="campaigns")
    donations = relationship("Donation", back_populates="campaign") 