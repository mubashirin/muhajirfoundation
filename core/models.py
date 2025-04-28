from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from core.database import Base

class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    api_key = Column(String, unique=True, nullable=False)
    api_secret = Column(String, nullable=False)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __str__(self):
        return f"{self.name} ({self.api_key})" 