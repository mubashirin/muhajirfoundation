# Содержимое admin.py переносится сюда полностью 

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from core.database import get_db
from users.models import User
from fund.models import FundInfo, SocialLink, BankDetail
from feedback.models import Feedback
from feedback import schemas
from donations.models import DonationCampaign, Wallet
from publications.models import Publication, PublicationImage, PublicationVideo
from publications.schemas import PublicationCreate, PublicationUpdate
from core.security import verify_password, create_access_token, get_password_hash
from datetime import datetime, timedelta
from jose import JWTError, jwt
from core.config import get_settings
from pydantic import BaseModel, UUID4
from decimal import Decimal
from auth.router import router as auth_router
from feedback import crud
from feedback.schemas import FeedbackCreate, FeedbackUpdate, FeedbackRead
import random
import string
import requests
from tgusers.routes import router as tgusers_router
from admin.deps import get_current_admin
from users.schemas import UserCreate, UserUpdate
from fund.schemas import FundInfoCreate, FundInfoUpdate
from . import users, fund, publications, feedback, donations
from .tg import router as tg_router

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")

# ... (весь остальной код admin.py, как в git show) ... 

def init_admin_routes(app: FastAPI):
    app.include_router(auth_router, prefix=settings.API_V1_STR)
    app.include_router(users.router)
    app.include_router(fund.router)
    app.include_router(publications.router)
    app.include_router(feedback.router)
    app.include_router(donations.router)
    app.include_router(tg_router)
    app.include_router(tgusers_router) 