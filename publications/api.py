from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from .models import Publication as PublicationModel
from .schemas import Publication
from core.database import get_db

router = APIRouter(prefix="/api/v1/publications", tags=["publications"])

@router.get("/", response_model=List[Publication])
def list_publications(db: Session = Depends(get_db)):
    return db.query(PublicationModel).all() 