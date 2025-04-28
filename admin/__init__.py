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
from admin.tg import router as tg_router

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")

# ... (весь остальной код admin.py, как в git show) ... 

def init_admin_routes(app: FastAPI):
    app.include_router(auth_router, prefix=settings.API_V1_STR)
    app.include_router(tg_router)
    app.include_router(tgusers_router)

    # Users
    @app.get("/admin/users", response_model=List[dict], tags=["admin"])
    async def get_users(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        users = db.query(User).all()
        return [{"id": user.id, "email": user.email, "full_name": user.full_name, "is_active": user.is_active, "is_superuser": user.is_superuser} for user in users]

    @app.get("/admin/users/{user_id}", response_model=dict, tags=["admin"])
    async def get_user(user_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"id": user.id, "email": user.email, "full_name": user.full_name, "is_active": user.is_active, "is_superuser": user.is_superuser}

    @app.post("/admin/users", tags=["admin"])
    async def create_user(
        user_data: UserCreate,
        current_admin: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
    ):
        if db.query(User).filter(User.email == user_data.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        hashed_password = get_password_hash(user_data.password)
        user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            is_active=user_data.is_active,
            is_superuser=user_data.is_superuser
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return {"id": user.id, "email": user.email, "full_name": user.full_name, "is_active": user.is_active, "is_superuser": user.is_superuser}

    @app.put("/admin/users/{user_id}", response_model=dict, tags=["admin"])
    async def update_user(user_id: int, user_data: UserUpdate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user_data.email and user_data.email != user.email:
            if db.query(User).filter(User.email == user_data.email).first():
                raise HTTPException(status_code=400, detail="Email already registered")
            user.email = user_data.email
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        if user_data.is_active is not None:
            user.is_active = user_data.is_active
        if user_data.is_superuser is not None:
            user.is_superuser = user_data.is_superuser
        db.commit()
        db.refresh(user)
        return {"id": user.id, "email": user.email, "full_name": user.full_name, "is_active": user.is_active, "is_superuser": user.is_superuser}

    @app.delete("/admin/users/{user_id}", tags=["admin"])
    async def delete_user(user_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        db.delete(user)
        db.commit()
        return {"message": "User deleted successfully"}

    # Fund Info
    @app.get("/admin/fund-info/list", response_model=List[dict], tags=["admin"])
    async def get_fund_info(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        fund_info = db.query(FundInfo).all()
        return [{"id": info.id, "name": info.name, "description": info.description, "address": info.address, "phone": info.phone, "email": info.email, "is_active": info.is_active} for info in fund_info]

    @app.get("/admin/fund-info/{fund_id}", response_model=dict, tags=["admin"])
    async def get_fund_info(fund_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        fund_info = db.query(FundInfo).filter(FundInfo.id == fund_id).first()
        if not fund_info:
            raise HTTPException(status_code=404, detail="Fund info not found")
        return {"id": fund_info.id, "name": fund_info.name, "description": fund_info.description, "address": fund_info.address, "phone": fund_info.phone, "email": fund_info.email, "is_active": fund_info.is_active}

    @app.post("/admin/fund-info", response_model=dict, tags=["admin"])
    async def create_fund_info(fund_data: FundInfoCreate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        fund_info = FundInfo(**fund_data.dict())
        db.add(fund_info)
        db.commit()
        db.refresh(fund_info)
        return {"id": fund_info.id, "name": fund_info.name, "description": fund_info.description, "address": fund_info.address, "phone": fund_info.phone, "email": fund_info.email, "is_active": fund_info.is_active}

    @app.put("/admin/fund-info/{fund_id}", response_model=dict, tags=["admin"])
    async def update_fund_info(fund_id: int, fund_data: FundInfoUpdate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        fund_info = db.query(FundInfo).filter(FundInfo.id == fund_id).first()
        if not fund_info:
            raise HTTPException(status_code=404, detail="Fund info not found")
        for field, value in fund_data.dict(exclude_unset=True).items():
            setattr(fund_info, field, value)
        db.commit()
        db.refresh(fund_info)
        return {"id": fund_info.id, "name": fund_info.name, "description": fund_info.description, "address": fund_info.address, "phone": fund_info.phone, "email": fund_info.email, "is_active": fund_info.is_active}

    @app.delete("/admin/fund-info/{fund_id}", tags=["admin"])
    async def delete_fund_info(fund_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        fund_info = db.query(FundInfo).filter(FundInfo.id == fund_id).first()
        if not fund_info:
            raise HTTPException(status_code=404, detail="Fund info not found")
        db.delete(fund_info)
        db.commit()
        return {"message": "Fund info deleted successfully"}

    # Publications
    @app.get("/admin/publications", response_model=List[dict], tags=["admin"])
    async def get_publications(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        publications = db.query(Publication).all()
        return [{"id": pub.id, "title": pub.title, "content": pub.content, "is_active": pub.is_active} for pub in publications]

    @app.get("/admin/publications/{publication_id}", response_model=dict, tags=["admin"])
    async def get_publication(publication_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        publication = db.query(Publication).filter(Publication.id == publication_id).first()
        if not publication:
            raise HTTPException(status_code=404, detail="Publication not found")
        return {"id": publication.id, "title": publication.title, "content": publication.content, "is_active": publication.is_active}

    @app.post("/admin/publications", response_model=dict, tags=["admin"])
    async def create_publication(publication_data: PublicationCreate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        publication = Publication(**publication_data.dict())
        db.add(publication)
        db.commit()
        db.refresh(publication)
        return {"id": publication.id, "title": publication.title, "content": publication.content, "is_active": publication.is_active}

    @app.put("/admin/publications/{publication_id}", response_model=dict, tags=["admin"])
    async def update_publication(publication_id: int, publication_data: PublicationUpdate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        publication = db.query(Publication).filter(Publication.id == publication_id).first()
        if not publication:
            raise HTTPException(status_code=404, detail="Publication not found")
        for field, value in publication_data.dict(exclude_unset=True).items():
            setattr(publication, field, value)
        db.commit()
        db.refresh(publication)
        return {"id": publication.id, "title": publication.title, "content": publication.content, "is_active": publication.is_active}

    @app.delete("/admin/publications/{publication_id}", tags=["admin"])
    async def delete_publication(publication_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        publication = db.query(Publication).filter(Publication.id == publication_id).first()
        if not publication:
            raise HTTPException(status_code=404, detail="Publication not found")
        db.delete(publication)
        db.commit()
        return {"message": "Publication deleted successfully"}

    # Feedback
    @app.get("/admin/feedback", response_model=List[FeedbackRead], tags=["admin"])
    async def get_feedback(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        return crud.get_feedback(db)

    @app.get("/admin/feedback/{feedback_id}", response_model=FeedbackRead, tags=["admin"])
    async def get_feedback_item(feedback_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        feedback = crud.get_feedback_item(db, feedback_id)
        if not feedback:
            raise HTTPException(status_code=404, detail="Feedback not found")
        return feedback

    @app.post("/admin/feedback", response_model=FeedbackRead, tags=["admin"])
    async def create_feedback(feedback_data: FeedbackCreate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        return crud.create_feedback(db, feedback_data)

    @app.put("/admin/feedback/{feedback_id}", response_model=FeedbackRead, tags=["admin"])
    async def update_feedback(feedback_id: int, feedback_data: FeedbackUpdate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        feedback = crud.update_feedback(db, feedback_id, feedback_data)
        if not feedback:
            raise HTTPException(status_code=404, detail="Feedback not found")
        return feedback

    @app.delete("/admin/feedback/{feedback_id}", tags=["admin"])
    async def delete_feedback(feedback_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        if not crud.delete_feedback(db, feedback_id):
            raise HTTPException(status_code=404, detail="Feedback not found")
        return {"message": "Feedback deleted successfully"}

    # Donation Campaigns
    @app.get("/admin/campaigns", response_model=List[dict], tags=["admin"])
    async def get_campaigns(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        campaigns = db.query(DonationCampaign).all()
        return [{"id": camp.id, "title": camp.title, "description": camp.description, "goal": camp.goal, "current": camp.current, "is_active": camp.is_active} for camp in campaigns]

    @app.get("/admin/campaigns/{campaign_id}", response_model=dict, tags=["admin"])
    async def get_campaign(campaign_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        campaign = db.query(DonationCampaign).filter(DonationCampaign.id == campaign_id).first()
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        return {"id": campaign.id, "title": campaign.title, "description": campaign.description, "goal": campaign.goal, "current": campaign.current, "is_active": campaign.is_active}

    @app.post("/admin/campaigns", response_model=dict, tags=["admin"])
    async def create_campaign(campaign_data: dict, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        campaign = DonationCampaign(**campaign_data)
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        return {"id": campaign.id, "title": campaign.title, "description": campaign.description, "goal": campaign.goal, "current": campaign.current, "is_active": campaign.is_active}

    @app.put("/admin/campaigns/{campaign_id}", response_model=dict, tags=["admin"])
    async def update_campaign(campaign_id: int, campaign_data: dict, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        campaign = db.query(DonationCampaign).filter(DonationCampaign.id == campaign_id).first()
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        for field, value in campaign_data.items():
            setattr(campaign, field, value)
        db.commit()
        db.refresh(campaign)
        return {"id": campaign.id, "title": campaign.title, "description": campaign.description, "goal": campaign.goal, "current": campaign.current, "is_active": campaign.is_active}

    @app.delete("/admin/campaigns/{campaign_id}", tags=["admin"])
    async def delete_campaign(campaign_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        campaign = db.query(DonationCampaign).filter(DonationCampaign.id == campaign_id).first()
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        db.delete(campaign)
        db.commit()
        return {"message": "Campaign deleted successfully"}

    # Wallets
    @app.get("/admin/wallets", response_model=List[dict], tags=["admin"])
    async def get_wallets(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        wallets = db.query(Wallet).all()
        return [{"id": wallet.id, "address": wallet.address, "type": wallet.type, "is_active": wallet.is_active} for wallet in wallets]

    @app.get("/admin/wallets/{wallet_id}", response_model=dict, tags=["admin"])
    async def get_wallet(wallet_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        return {"id": wallet.id, "address": wallet.address, "type": wallet.type, "is_active": wallet.is_active}

    @app.post("/admin/wallets", response_model=dict, tags=["admin"])
    async def create_wallet(wallet_data: dict, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        wallet = Wallet(**wallet_data)
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
        return {"id": wallet.id, "address": wallet.address, "type": wallet.type, "is_active": wallet.is_active}

    @app.put("/admin/wallets/{wallet_id}", response_model=dict, tags=["admin"])
    async def update_wallet(wallet_id: int, wallet_data: dict, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        for field, value in wallet_data.items():
            setattr(wallet, field, value)
        db.commit()
        db.refresh(wallet)
        return {"id": wallet.id, "address": wallet.address, "type": wallet.type, "is_active": wallet.is_active}

    @app.delete("/admin/wallets/{wallet_id}", tags=["admin"])
    async def delete_wallet(wallet_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        db.delete(wallet)
        db.commit()
        return {"message": "Wallet deleted successfully"}

    # Social Links
    @app.get("/admin/social-links", response_model=List[dict], tags=["admin"])
    async def get_social_links(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        links = db.query(SocialLink).all()
        return [{"id": link.id, "platform": link.platform, "url": link.url, "is_active": link.is_active} for link in links]

    @app.get("/admin/social-links/{link_id}", response_model=dict, tags=["admin"])
    async def get_social_link(link_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        link = db.query(SocialLink).filter(SocialLink.id == link_id).first()
        if not link:
            raise HTTPException(status_code=404, detail="Social link not found")
        return {"id": link.id, "platform": link.platform, "url": link.url, "is_active": link.is_active}

    @app.post("/admin/social-links", response_model=dict, tags=["admin"])
    async def create_social_link(link_data: dict, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        link = SocialLink(**link_data)
        db.add(link)
        db.commit()
        db.refresh(link)
        return {"id": link.id, "platform": link.platform, "url": link.url, "is_active": link.is_active}

    @app.put("/admin/social-links/{link_id}", response_model=dict, tags=["admin"])
    async def update_social_link(link_id: int, link_data: dict, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        link = db.query(SocialLink).filter(SocialLink.id == link_id).first()
        if not link:
            raise HTTPException(status_code=404, detail="Social link not found")
        for field, value in link_data.items():
            setattr(link, field, value)
        db.commit()
        db.refresh(link)
        return {"id": link.id, "platform": link.platform, "url": link.url, "is_active": link.is_active}

    @app.delete("/admin/social-links/{link_id}", tags=["admin"])
    async def delete_social_link(link_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        link = db.query(SocialLink).filter(SocialLink.id == link_id).first()
        if not link:
            raise HTTPException(status_code=404, detail="Social link not found")
        db.delete(link)
        db.commit()
        return {"message": "Social link deleted successfully"}

    # Bank Details
    @app.get("/admin/bank-details", response_model=List[dict], tags=["admin"])
    async def get_bank_details(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        details = db.query(BankDetail).all()
        return [{"id": detail.id, "bank_name": detail.bank_name, "account_number": detail.account_number, "is_active": detail.is_active} for detail in details]

    @app.get("/admin/bank-details/{detail_id}", response_model=dict, tags=["admin"])
    async def get_bank_detail(detail_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        detail = db.query(BankDetail).filter(BankDetail.id == detail_id).first()
        if not detail:
            raise HTTPException(status_code=404, detail="Bank detail not found")
        return {"id": detail.id, "bank_name": detail.bank_name, "account_number": detail.account_number, "is_active": detail.is_active}

    @app.post("/admin/bank-details", response_model=dict, tags=["admin"])
    async def create_bank_detail(detail_data: dict, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        detail = BankDetail(**detail_data)
        db.add(detail)
        db.commit()
        db.refresh(detail)
        return {"id": detail.id, "bank_name": detail.bank_name, "account_number": detail.account_number, "is_active": detail.is_active}

    @app.put("/admin/bank-details/{detail_id}", response_model=dict, tags=["admin"])
    async def update_bank_detail(detail_id: int, detail_data: dict, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        detail = db.query(BankDetail).filter(BankDetail.id == detail_id).first()
        if not detail:
            raise HTTPException(status_code=404, detail="Bank detail not found")
        for field, value in detail_data.items():
            setattr(detail, field, value)
        db.commit()
        db.refresh(detail)
        return {"id": detail.id, "bank_name": detail.bank_name, "account_number": detail.account_number, "is_active": detail.is_active}

    @app.delete("/admin/bank-details/{detail_id}", tags=["admin"])
    async def delete_bank_detail(detail_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        detail = db.query(BankDetail).filter(BankDetail.id == detail_id).first()
        if not detail:
            raise HTTPException(status_code=404, detail="Bank detail not found")
        db.delete(detail)
        db.commit()
        return {"message": "Bank detail deleted successfully"} 