from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base

class Publication(Base):
    __tablename__ = "publications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    slug = Column(String, nullable=False, unique=True)
    photo = Column(String, nullable=True)
    text = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    is_fundraising = Column(Boolean, default=False)
    views = Column(Integer, default=0)
    source_link = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    ipfs_link = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __str__(self):
        return self.title

class PublicationImage(Base):
    __tablename__ = "publication_images"

    id = Column(Integer, primary_key=True, index=True)
    publication_id = Column(Integer, ForeignKey("publications.id", ondelete="CASCADE"), nullable=False)
    image = Column(String, nullable=False)
    publication = relationship("Publication", backref="images")

class PublicationVideo(Base):
    __tablename__ = "publication_videos"

    id = Column(Integer, primary_key=True, index=True)
    publication_id = Column(Integer, ForeignKey("publications.id", ondelete="CASCADE"), nullable=False)
    video = Column(String, nullable=False)
    publication = relationship("Publication", backref="videos")