from sqlalchemy.orm import Session
from . import models, schemas
from core.config import get_settings
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pathlib import Path
from pydantic import EmailStr

def create_feedback(db: Session, feedback: schemas.FeedbackCreate):
    db_feedback = models.Feedback(**feedback.model_dump())
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

def get_feedback(db: Session, feedback_id: int):
    return db.query(models.Feedback).filter(models.Feedback.id == feedback_id).first()

def get_feedbacks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Feedback).offset(skip).limit(limit).all()

def update_feedback(db: Session, feedback_id: int, feedback: schemas.FeedbackUpdate):
    db_feedback = get_feedback(db, feedback_id)
    if not db_feedback:
        return None
    
    update_data = feedback.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_feedback, field, value)
    
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

def delete_feedback(db: Session, feedback_id: int):
    db_feedback = get_feedback(db, feedback_id)
    if not db_feedback:
        return False
    
    db.delete(db_feedback)
    db.commit()
    return True

async def send_feedback_email(feedback: models.Feedback):
    settings = get_settings()
    conf = ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
        TEMPLATE_FOLDER=Path(__file__).parent.parent / 'templates'
    )
    
    message = MessageSchema(
        subject="Спасибо за ваш отзыв!",
        recipients=[feedback.email],
        template_body={
            "name": feedback.name,
            "message": feedback.message
        },
        subtype="html"
    )
    
    fm = FastMail(conf)
    await fm.send_message(message, template_name="feedback_email.html")
