from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from users.models import User
from feedback.models import Feedback
from feedback.schemas import FeedbackCreate, FeedbackUpdate, FeedbackRead
from admin.deps import get_current_admin
from admin.crud import BaseCRUD

router = APIRouter(prefix="/admin/feedback", tags=["admin-feedback"])

feedback_crud = BaseCRUD(Feedback)

@router.get("/", response_model=List[FeedbackRead])
async def get_feedback(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    return feedback_crud.get_multi(db, skip=skip, limit=limit)

@router.get("/{feedback_id}", response_model=FeedbackRead)
async def get_feedback_item(
    feedback_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    feedback = feedback_crud.get(db, id=feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return feedback

@router.post("/", response_model=FeedbackRead)
async def create_feedback(
    feedback_in: FeedbackCreate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return feedback_crud.create(db, obj_in=feedback_in)

@router.put("/{feedback_id}", response_model=FeedbackRead)
async def update_feedback(
    feedback_id: int,
    feedback_in: FeedbackUpdate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    feedback = feedback_crud.get(db, id=feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return feedback_crud.update(db, db_obj=feedback, obj_in=feedback_in)

@router.delete("/{feedback_id}")
async def delete_feedback(
    feedback_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    feedback = feedback_crud.get(db, id=feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    feedback_crud.remove(db, id=feedback_id)
    return {"message": "Feedback deleted successfully"} 