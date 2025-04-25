from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from . import crud, schemas

router = APIRouter(prefix="/feedback", tags=["feedback"])

@router.post("/", response_model=schemas.Feedback)
def create_feedback(
    feedback: schemas.FeedbackCreate,
    db: Session = Depends(get_db)
):
    """Создать новый отзыв"""
    return crud.create_feedback(db=db, feedback=feedback)
