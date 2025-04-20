from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base

class FundInfo(Base):
    __tablename__ = "fund_info"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    address = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    social_links = relationship("SocialLink", back_populates="fund", cascade="all, delete-orphan")
    bank_details = relationship("BankDetail", back_populates="fund", cascade="all, delete-orphan")

    def __str__(self):
        return self.name

class SocialLink(Base):
    __tablename__ = "social_links"

    id = Column(Integer, primary_key=True, index=True)
    fund_id = Column(Integer, ForeignKey("fund_info.id", ondelete="CASCADE"), nullable=False)
    platform = Column(String, nullable=False)  # например: facebook, twitter, instagram
    url = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    fund = relationship("FundInfo", back_populates="social_links")

    def __str__(self):
        return f"{self.platform}: {self.url}"

class BankDetail(Base):
    __tablename__ = "bank_details"

    id = Column(Integer, primary_key=True, index=True)
    fund_id = Column(Integer, ForeignKey("fund_info.id", ondelete="CASCADE"), nullable=False)
    bank_name = Column(String, nullable=False)
    account_number = Column(String, nullable=False)
    swift_code = Column(String, nullable=True)
    iban = Column(String, nullable=True)
    currency = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    fund = relationship("FundInfo", back_populates="bank_details")

    def __str__(self):
        return f"{self.bank_name} ({self.currency})"