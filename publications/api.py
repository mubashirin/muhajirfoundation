from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from .models import Publication as PublicationModel, PublicationImage, PublicationVideo
from .schemas import Publication
from core.database import get_db

router = APIRouter(prefix="/api/v1/publications", tags=["publications"])

@router.get("/", response_model=List[Publication])
def list_publications(db: Session = Depends(get_db)):
    publications = db.query(PublicationModel).all()
    result = []
    for pub in publications:
        images = db.query(PublicationImage).filter(PublicationImage.publication_id == pub.id).all()
        videos = db.query(PublicationVideo).filter(PublicationVideo.publication_id == pub.id).all()
        pub.images = images
        pub.videos = videos
        result.append(pub)
    return result 