from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from users.models import User
from fund.models import FundInfo, SocialLink, BankDetail
from feedback.models import Feedback
from donations.models import DonationCampaign, Wallet
from publications.models import Publication
from publications.schemas import PublicationCreate, PublicationUpdate
from core.security import verify_password, create_access_token, get_password_hash
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pathlib import Path
from jose import JWTError, jwt
from core.config import get_settings
from pydantic import BaseModel, UUID4
from decimal import Decimal

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
templates = Jinja2Templates(directory="templates")

# Pydantic модели для валидации данных
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False

class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

class FundInfoCreate(BaseModel):
    name: str
    description: str
    address: str
    phone: str
    email: str
    is_active: bool = True

class FundInfoUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None

class SocialLinkCreate(BaseModel):
    fund_id: int
    platform: str
    url: str

class SocialLinkUpdate(BaseModel):
    platform: Optional[str] = None
    url: Optional[str] = None

class BankDetailCreate(BaseModel):
    fund_id: int
    bank_name: str
    account_number: str
    swift_code: Optional[str] = None
    iban: Optional[str] = None
    currency: str

class BankDetailUpdate(BaseModel):
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    swift_code: Optional[str] = None
    iban: Optional[str] = None
    currency: Optional[str] = None

class FeedbackUpdate(BaseModel):
    is_read: bool

class CampaignCreate(BaseModel):
    title: str
    description: Optional[str] = None
    target_amount: Decimal = 0
    is_active: bool = True

class CampaignUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    target_amount: Optional[Decimal] = None
    is_active: Optional[bool] = None

class WalletCreate(BaseModel):
    name: str
    campaign_id: int
    usdt_trc20: Optional[str] = None
    bch: Optional[str] = None
    eth: Optional[str] = None
    btc: Optional[str] = None

class WalletUpdate(BaseModel):
    name: Optional[str] = None
    usdt_trc20: Optional[str] = None
    bch: Optional[str] = None
    eth: Optional[str] = None
    btc: Optional[str] = None

class PublicationCreate(BaseModel):
    title: str
    slug: str
    photo: str
    text: str
    is_active: bool = True
    is_fundraising: bool = False
    source_link: Optional[str] = None

class PublicationUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    photo: Optional[str] = None
    text: Optional[str] = None
    is_active: Optional[bool] = None
    is_fundraising: Optional[bool] = None
    source_link: Optional[str] = None

async def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.is_superuser:
        raise credentials_exception
    return user

def init_admin_routes(app: FastAPI):
    @app.get("/admin/", response_class=HTMLResponse)
    async def admin_root(request: Request):
        return templates.TemplateResponse("admin/index.html", {"request": request})

    @app.get("/admin/login", response_class=HTMLResponse)
    async def admin_login_page(request: Request):
        return templates.TemplateResponse("admin/login.html", {"request": request})

    @app.post("/admin/login")
    async def admin_login(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
        user = db.query(User).filter(User.email == email).first()
        if not user or not user.is_superuser or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = create_access_token(subject=user.email)
        return {"access_token": access_token, "token_type": "bearer"}

    # Users endpoints
    @app.get("/admin/users", response_model=List[dict])
    async def get_users(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        users = db.query(User).all()
        return [{"id": user.id, "email": user.email, "full_name": user.full_name, "is_active": user.is_active, "is_superuser": user.is_superuser} for user in users]

    @app.get("/admin/users/{user_id}", response_model=dict)
    async def get_user(user_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"id": user.id, "email": user.email, "full_name": user.full_name, "is_active": user.is_active, "is_superuser": user.is_superuser}

    @app.post("/admin/users", response_model=dict)
    async def create_user(user_data: UserCreate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        db_user = User(
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            is_active=user_data.is_active,
            is_superuser=user_data.is_superuser
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return {"id": db_user.id, "email": db_user.email, "full_name": db_user.full_name, "is_active": db_user.is_active, "is_superuser": db_user.is_superuser}

    @app.put("/admin/users/{user_id}", response_model=dict)
    async def update_user(user_id: int, user_data: UserUpdate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        for field, value in user_data.dict(exclude_unset=True).items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        return {"id": user.id, "email": user.email, "full_name": user.full_name, "is_active": user.is_active, "is_superuser": user.is_superuser}

    @app.delete("/admin/users/{user_id}")
    async def delete_user(user_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        db.delete(user)
        db.commit()
        return {"message": "User deleted"}

    # Fund Info endpoints
    @app.get("/admin/fund-info/list", response_model=List[dict])
    async def get_fund_info(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        fund_info = db.query(FundInfo).all()
        return [{"id": info.id, "name": info.name, "description": info.description, "address": info.address, "phone": info.phone, "email": info.email, "is_active": info.is_active} for info in fund_info]

    @app.get("/admin/fund-info/{fund_id}", response_model=dict)
    async def get_fund_info(fund_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        fund_info = db.query(FundInfo).filter(FundInfo.id == fund_id).first()
        if not fund_info:
            raise HTTPException(status_code=404, detail="Fund info not found")
        return {"id": fund_info.id, "name": fund_info.name, "description": fund_info.description, "address": fund_info.address, "phone": fund_info.phone, "email": fund_info.email, "is_active": fund_info.is_active}

    @app.post("/admin/fund-info", response_model=dict)
    async def create_fund_info(fund_data: FundInfoCreate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        fund_info = FundInfo(**fund_data.dict())
        db.add(fund_info)
        db.commit()
        db.refresh(fund_info)
        return {"id": fund_info.id, "name": fund_info.name, "description": fund_info.description, "address": fund_info.address, "phone": fund_info.phone, "email": fund_info.email, "is_active": fund_info.is_active}

    @app.put("/admin/fund-info/{fund_id}", response_model=dict)
    async def update_fund_info(fund_id: int, fund_data: FundInfoUpdate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        fund_info = db.query(FundInfo).filter(FundInfo.id == fund_id).first()
        if not fund_info:
            raise HTTPException(status_code=404, detail="Fund info not found")
        
        for field, value in fund_data.dict(exclude_unset=True).items():
            setattr(fund_info, field, value)
        
        db.commit()
        db.refresh(fund_info)
        return {"id": fund_info.id, "name": fund_info.name, "description": fund_info.description, "address": fund_info.address, "phone": fund_info.phone, "email": fund_info.email, "is_active": fund_info.is_active}

    @app.delete("/admin/fund-info/{fund_id}")
    async def delete_fund_info(fund_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        fund_info = db.query(FundInfo).filter(FundInfo.id == fund_id).first()
        if not fund_info:
            raise HTTPException(status_code=404, detail="Fund info not found")
        
        db.delete(fund_info)
        db.commit()
        return {"message": "Fund info deleted"}

    # Social Links endpoints
    @app.get("/admin/social-links", response_model=List[dict])
    async def get_social_links(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        social_links = db.query(SocialLink).all()
        return [{"id": link.id, "fund_id": link.fund_id, "platform": link.platform, "url": link.url} for link in social_links]

    @app.get("/admin/social-links/{link_id}", response_model=dict)
    async def get_social_link(link_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        social_link = db.query(SocialLink).filter(SocialLink.id == link_id).first()
        if not social_link:
            raise HTTPException(status_code=404, detail="Social link not found")
        return {"id": social_link.id, "fund_id": social_link.fund_id, "platform": social_link.platform, "url": social_link.url}

    @app.post("/admin/social-links", response_model=dict)
    async def create_social_link(link_data: SocialLinkCreate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        social_link = SocialLink(**link_data.dict())
        db.add(social_link)
        db.commit()
        db.refresh(social_link)
        return {"id": social_link.id, "fund_id": social_link.fund_id, "platform": social_link.platform, "url": social_link.url}

    @app.put("/admin/social-links/{link_id}", response_model=dict)
    async def update_social_link(link_id: int, link_data: SocialLinkUpdate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        social_link = db.query(SocialLink).filter(SocialLink.id == link_id).first()
        if not social_link:
            raise HTTPException(status_code=404, detail="Social link not found")
        
        for field, value in link_data.dict(exclude_unset=True).items():
            setattr(social_link, field, value)
        
        db.commit()
        db.refresh(social_link)
        return {"id": social_link.id, "fund_id": social_link.fund_id, "platform": social_link.platform, "url": social_link.url}

    @app.delete("/admin/social-links/{link_id}")
    async def delete_social_link(link_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        social_link = db.query(SocialLink).filter(SocialLink.id == link_id).first()
        if not social_link:
            raise HTTPException(status_code=404, detail="Social link not found")
        
        db.delete(social_link)
        db.commit()
        return {"message": "Social link deleted"}

    # Bank Details endpoints
    @app.get("/admin/bank-details", response_model=List[dict])
    async def get_bank_details(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        bank_details = db.query(BankDetail).all()
        return [{"id": detail.id, "fund_id": detail.fund_id, "bank_name": detail.bank_name, "account_number": detail.account_number, "swift_code": detail.swift_code, "iban": detail.iban, "currency": detail.currency} for detail in bank_details]

    @app.get("/admin/bank-details/{detail_id}", response_model=dict)
    async def get_bank_detail(detail_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        bank_detail = db.query(BankDetail).filter(BankDetail.id == detail_id).first()
        if not bank_detail:
            raise HTTPException(status_code=404, detail="Bank detail not found")
        return {"id": bank_detail.id, "fund_id": bank_detail.fund_id, "bank_name": bank_detail.bank_name, "account_number": bank_detail.account_number, "swift_code": bank_detail.swift_code, "iban": bank_detail.iban, "currency": bank_detail.currency}

    @app.post("/admin/bank-details", response_model=dict)
    async def create_bank_detail(detail_data: BankDetailCreate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        bank_detail = BankDetail(**detail_data.dict())
        db.add(bank_detail)
        db.commit()
        db.refresh(bank_detail)
        return {"id": bank_detail.id, "fund_id": bank_detail.fund_id, "bank_name": bank_detail.bank_name, "account_number": bank_detail.account_number, "swift_code": bank_detail.swift_code, "iban": bank_detail.iban, "currency": bank_detail.currency}

    @app.put("/admin/bank-details/{detail_id}", response_model=dict)
    async def update_bank_detail(detail_id: int, detail_data: BankDetailUpdate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        bank_detail = db.query(BankDetail).filter(BankDetail.id == detail_id).first()
        if not bank_detail:
            raise HTTPException(status_code=404, detail="Bank detail not found")
        
        for field, value in detail_data.dict(exclude_unset=True).items():
            setattr(bank_detail, field, value)
        
        db.commit()
        db.refresh(bank_detail)
        return {"id": bank_detail.id, "fund_id": bank_detail.fund_id, "bank_name": bank_detail.bank_name, "account_number": bank_detail.account_number, "swift_code": bank_detail.swift_code, "iban": bank_detail.iban, "currency": bank_detail.currency}

    @app.delete("/admin/bank-details/{detail_id}")
    async def delete_bank_detail(detail_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        bank_detail = db.query(BankDetail).filter(BankDetail.id == detail_id).first()
        if not bank_detail:
            raise HTTPException(status_code=404, detail="Bank detail not found")
        
        db.delete(bank_detail)
        db.commit()
        return {"message": "Bank detail deleted"}

    # Feedback endpoints
    @app.get("/admin/feedback", response_model=List[dict])
    async def get_feedback(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        feedback = db.query(Feedback).all()
        return [{"id": f.id, "name": f.name, "email": f.email, "message": f.message, "is_read": f.is_read} for f in feedback]

    @app.get("/admin/feedback/{feedback_id}", response_model=dict)
    async def get_feedback(feedback_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not feedback:
            raise HTTPException(status_code=404, detail="Feedback not found")
        return {"id": feedback.id, "name": feedback.name, "email": feedback.email, "message": feedback.message, "is_read": feedback.is_read}

    @app.put("/admin/feedback/{feedback_id}", response_model=dict)
    async def update_feedback(feedback_id: int, feedback_data: FeedbackUpdate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not feedback:
            raise HTTPException(status_code=404, detail="Feedback not found")
        
        for field, value in feedback_data.dict(exclude_unset=True).items():
            setattr(feedback, field, value)
        
        db.commit()
        db.refresh(feedback)
        return {"id": feedback.id, "name": feedback.name, "email": feedback.email, "message": feedback.message, "is_read": feedback.is_read}

    @app.delete("/admin/feedback/{feedback_id}")
    async def delete_feedback(feedback_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not feedback:
            raise HTTPException(status_code=404, detail="Feedback not found")
        
        db.delete(feedback)
        db.commit()
        return {"message": "Feedback deleted"}

    # Campaign endpoints
    @app.get("/admin/campaigns", response_model=List[dict])
    async def get_campaigns(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        campaigns = db.query(DonationCampaign).all()
        return [{"id": c.id, "uuid": str(c.uuid), "title": c.title, "description": c.description, "is_active": c.is_active} for c in campaigns]

    @app.get("/admin/campaigns/{campaign_id}", response_model=dict)
    async def get_campaign(campaign_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        campaign = db.query(DonationCampaign).filter(DonationCampaign.id == campaign_id).first()
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        return {"id": campaign.id, "uuid": str(campaign.uuid), "title": campaign.title, "description": campaign.description, "is_active": campaign.is_active}

    @app.post("/admin/campaigns", response_model=dict)
    async def create_campaign(campaign_data: CampaignCreate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        campaign = DonationCampaign(**campaign_data.dict())
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        return {"id": campaign.id, "uuid": str(campaign.uuid), "title": campaign.title, "description": campaign.description, "is_active": campaign.is_active}

    @app.put("/admin/campaigns/{campaign_id}", response_model=dict)
    async def update_campaign(campaign_id: int, campaign_data: CampaignUpdate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        campaign = db.query(DonationCampaign).filter(DonationCampaign.id == campaign_id).first()
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        for field, value in campaign_data.dict(exclude_unset=True).items():
            setattr(campaign, field, value)
        
        db.commit()
        db.refresh(campaign)
        return {"id": campaign.id, "uuid": str(campaign.uuid), "title": campaign.title, "description": campaign.description, "is_active": campaign.is_active}

    @app.delete("/admin/campaigns/{campaign_id}")
    async def delete_campaign(campaign_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        campaign = db.query(DonationCampaign).filter(DonationCampaign.id == campaign_id).first()
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        db.delete(campaign)
        db.commit()
        return {"message": "Campaign deleted"}

    # Wallet endpoints
    @app.get("/admin/wallets", response_model=List[dict])
    async def get_wallets(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        wallets = db.query(Wallet).all()
        return [{"id": w.id, "uuid": str(w.uuid), "name": w.name, "campaign_id": w.campaign_id, "usdt_trc20": w.usdt_trc20, "bch": w.bch, "eth": w.eth, "btc": w.btc} for w in wallets]

    @app.get("/admin/wallets/{wallet_id}", response_model=dict)
    async def get_wallet(wallet_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        return {"id": wallet.id, "uuid": str(wallet.uuid), "name": wallet.name, "campaign_id": wallet.campaign_id, "usdt_trc20": wallet.usdt_trc20, "bch": wallet.bch, "eth": wallet.eth, "btc": wallet.btc}

    @app.post("/admin/wallets", response_model=dict)
    async def create_wallet(wallet_data: WalletCreate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        wallet = Wallet(**wallet_data.dict())
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
        return {"id": wallet.id, "uuid": str(wallet.uuid), "name": wallet.name, "campaign_id": wallet.campaign_id, "usdt_trc20": wallet.usdt_trc20, "bch": wallet.bch, "eth": wallet.eth, "btc": wallet.btc}

    @app.put("/admin/wallets/{wallet_id}", response_model=dict)
    async def update_wallet(wallet_id: int, wallet_data: WalletUpdate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        
        for field, value in wallet_data.dict(exclude_unset=True).items():
            setattr(wallet, field, value)
        
        db.commit()
        db.refresh(wallet)
        return {"id": wallet.id, "uuid": str(wallet.uuid), "name": wallet.name, "campaign_id": wallet.campaign_id, "usdt_trc20": wallet.usdt_trc20, "bch": wallet.bch, "eth": wallet.eth, "btc": wallet.btc}

    @app.delete("/admin/wallets/{wallet_id}")
    async def delete_wallet(wallet_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        
        db.delete(wallet)
        db.commit()
        return {"message": "Wallet deleted"}

    # Publication endpoints
    @app.get("/admin/publications", response_model=List[dict])
    async def get_publications(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        publications = db.query(Publication).all()
        return [{"id": p.id, "title": p.title, "slug": p.slug, "photo": p.photo, "text": p.text, "is_active": p.is_active, "is_fundraising": p.is_fundraising, "views": p.views, "source_link": p.source_link} for p in publications]

    @app.get("/admin/publications/{publication_id}", response_model=dict)
    async def get_publication(publication_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        publication = db.query(Publication).filter(Publication.id == publication_id).first()
        if not publication:
            raise HTTPException(status_code=404, detail="Publication not found")
        return {"id": publication.id, "title": publication.title, "slug": publication.slug, "photo": publication.photo, "text": publication.text, "is_active": publication.is_active, "is_fundraising": publication.is_fundraising, "views": publication.views, "source_link": publication.source_link}

    @app.post("/admin/publications", response_model=dict)
    async def create_publication(publication_data: PublicationCreate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        publication = Publication(**publication_data.dict())
        db.add(publication)
        db.commit()
        db.refresh(publication)
        return {"id": publication.id, "title": publication.title, "slug": publication.slug, "photo": publication.photo, "text": publication.text, "is_active": publication.is_active, "is_fundraising": publication.is_fundraising, "views": publication.views, "source_link": publication.source_link}

    @app.put("/admin/publications/{publication_id}", response_model=dict)
    async def update_publication(publication_id: int, publication_data: PublicationUpdate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        publication = db.query(Publication).filter(Publication.id == publication_id).first()
        if not publication:
            raise HTTPException(status_code=404, detail="Publication not found")
        
        for field, value in publication_data.dict(exclude_unset=True).items():
            setattr(publication, field, value)
        
        db.commit()
        db.refresh(publication)
        return {"id": publication.id, "title": publication.title, "slug": publication.slug, "photo": publication.photo, "text": publication.text, "is_active": publication.is_active, "is_fundraising": publication.is_fundraising, "views": publication.views, "source_link": publication.source_link}

    @app.delete("/admin/publications/{publication_id}")
    async def delete_publication(publication_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        publication = db.query(Publication).filter(Publication.id == publication_id).first()
        if not publication:
            raise HTTPException(status_code=404, detail="Publication not found")
        
        db.delete(publication)
        db.commit()
        return {"message": "Publication deleted"}

    # Добавляем CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    ) 