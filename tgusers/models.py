from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, BigInteger
from sqlalchemy.orm import relationship
from core.database import Base

class TgUsers(Base):
    __tablename__ = "tg_users"

    id = Column(Integer, primary_key=True, index=True)
    id_telegram = Column(BigInteger, nullable=False)
    name = Column(String, nullable=False)
    uuid_id = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __str__(self):
        return f"{self.id_telegram} {self.name}"
