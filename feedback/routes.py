from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session

from core.database import get_db
from auth.dependencies import get_current_user
from users.models import User
from . import crud, schemas

router = APIRouter(prefix="/feedback", tags=["feedback"])

def get_admin_user(current_user: Annotated[User, Security(get_current_user)]):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions. Only admin can access this endpoint."
        )
    return current_user

@router.post("/", response_model=schemas.Feedback)
def create_feedback(
    feedback: schemas.FeedbackCreate,
    db: Session = Depends(get_db)
):
    return crud.create_feedback(db=db, feedback=feedback)

@router.get("/", response_model=List[schemas.Feedback])
def read_feedbacks(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud.get_feedbacks(db=db, skip=skip, limit=limit)

@router.get("/{feedback_id}", response_model=schemas.Feedback)
def read_feedback(
    feedback_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db_feedback = crud.get_feedback(db=db, feedback_id=feedback_id)
    if db_feedback is None:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return db_feedback

@router.put("/{feedback_id}", response_model=schemas.Feedback)
def update_feedback(
    feedback_id: int,
    feedback: schemas.FeedbackUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db_feedback = crud.update_feedback(db=db, feedback_id=feedback_id, feedback=feedback)
    if db_feedback is None:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return db_feedback

@router.delete("/{feedback_id}")
def delete_feedback(
    feedback_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if not crud.delete_feedback(db=db, feedback_id=feedback_id):
        raise HTTPException(status_code=404, detail="Feedback not found")
    return {"message": "Feedback deleted successfully"}

@router.post("/{feedback_id}/send-email", response_model=schemas.Feedback)
async def send_email(
    feedback_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    feedback = crud.get_feedback(db, feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
        
    await crud.send_feedback_email(feedback)
    return feedback
