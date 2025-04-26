from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from users.models import User
from fund.models import FundInfo, SocialLink, BankDetail
from feedback.models import Feedback
from feedback import schemas
from donations.models import DonationCampaign, Wallet
from publications.models import Publication
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

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")

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
    target_amount: Decimal
    wallet_id: Optional[int] = None
    is_active: bool = True

class CampaignUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    wallet_id: Optional[int] = None
    is_active: Optional[bool] = None

class WalletCreate(BaseModel):
    name: str
    usdt_trc20: Optional[str] = None
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
    if user is None:
        raise credentials_exception
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return user

def init_admin_routes(app: FastAPI):
    app.include_router(auth_router, prefix=settings.API_V1_STR)

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

    # Social Links
    @app.get("/admin/social-links", response_model=List[dict], tags=["admin"])
    async def get_social_links(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        links = db.query(SocialLink).all()
        return [{"id": link.id, "fund_id": link.fund_id, "platform": link.platform, "url": link.url} for link in links]

    @app.get("/admin/social-links/{link_id}", response_model=dict, tags=["admin"])
    async def get_social_link(link_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        link = db.query(SocialLink).filter(SocialLink.id == link_id).first()
        if not link:
            raise HTTPException(status_code=404, detail="Social link not found")
        return {"id": link.id, "fund_id": link.fund_id, "platform": link.platform, "url": link.url}

    @app.post("/admin/social-links", response_model=dict, tags=["admin"])
    async def create_social_link(link_data: SocialLinkCreate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        link = SocialLink(**link_data.dict())
        db.add(link)
        db.commit()
        db.refresh(link)
        return {"id": link.id, "fund_id": link.fund_id, "platform": link.platform, "url": link.url}

    @app.put("/admin/social-links/{link_id}", response_model=dict, tags=["admin"])
    async def update_social_link(link_id: int, link_data: SocialLinkUpdate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        link = db.query(SocialLink).filter(SocialLink.id == link_id).first()
        if not link:
            raise HTTPException(status_code=404, detail="Social link not found")
        
        for field, value in link_data.dict(exclude_unset=True).items():
            setattr(link, field, value)
        
        db.commit()
        db.refresh(link)
        return {"id": link.id, "fund_id": link.fund_id, "platform": link.platform, "url": link.url}

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
        return [{"id": detail.id, "fund_id": detail.fund_id, "bank_name": detail.bank_name, "account_number": detail.account_number, "swift_code": detail.swift_code, "iban": detail.iban, "currency": detail.currency} for detail in details]

    @app.get("/admin/bank-details/{detail_id}", response_model=dict, tags=["admin"])
    async def get_bank_detail(detail_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        detail = db.query(BankDetail).filter(BankDetail.id == detail_id).first()
        if not detail:
            raise HTTPException(status_code=404, detail="Bank detail not found")
        return {"id": detail.id, "fund_id": detail.fund_id, "bank_name": detail.bank_name, "account_number": detail.account_number, "swift_code": detail.swift_code, "iban": detail.iban, "currency": detail.currency}

    @app.post("/admin/bank-details", response_model=dict, tags=["admin"])
    async def create_bank_detail(detail_data: BankDetailCreate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        detail = BankDetail(**detail_data.dict())
        db.add(detail)
        db.commit()
        db.refresh(detail)
        return {"id": detail.id, "fund_id": detail.fund_id, "bank_name": detail.bank_name, "account_number": detail.account_number, "swift_code": detail.swift_code, "iban": detail.iban, "currency": detail.currency}

    @app.put("/admin/bank-details/{detail_id}", response_model=dict, tags=["admin"])
    async def update_bank_detail(detail_id: int, detail_data: BankDetailUpdate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        detail = db.query(BankDetail).filter(BankDetail.id == detail_id).first()
        if not detail:
            raise HTTPException(status_code=404, detail="Bank detail not found")
        
        for field, value in detail_data.dict(exclude_unset=True).items():
            setattr(detail, field, value)
        
        db.commit()
        db.refresh(detail)
        return {"id": detail.id, "fund_id": detail.fund_id, "bank_name": detail.bank_name, "account_number": detail.account_number, "swift_code": detail.swift_code, "iban": detail.iban, "currency": detail.currency}

    @app.delete("/admin/bank-details/{detail_id}", tags=["admin"])
    async def delete_bank_detail(detail_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        detail = db.query(BankDetail).filter(BankDetail.id == detail_id).first()
        if not detail:
            raise HTTPException(status_code=404, detail="Bank detail not found")
        db.delete(detail)
        db.commit()
        return {"message": "Bank detail deleted successfully"}

    # Feedback
    @app.get("/admin/feedback", response_model=List[dict], tags=["admin"])
    async def get_feedback(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        feedback = db.query(Feedback).all()
        return [{"id": fb.id, "name": fb.name, "email": fb.email, "message": fb.message, "is_read": fb.is_read, "created_at": fb.created_at} for fb in feedback]

    @app.get("/admin/feedback/{feedback_id}", response_model=dict, tags=["admin"])
    async def get_feedback(feedback_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not feedback:
            raise HTTPException(status_code=404, detail="Feedback not found")
        return {"id": feedback.id, "name": feedback.name, "email": feedback.email, "message": feedback.message, "is_read": feedback.is_read, "created_at": feedback.created_at}

    @app.put("/admin/feedback/{feedback_id}", response_model=FeedbackRead, tags=["admin"])
    async def update_feedback_status(
        feedback_id: int,
        feedback_update: FeedbackUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_admin),
    ):
        """
        Update feedback read status.
        """
        feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not feedback:
            raise HTTPException(status_code=404, detail="Feedback not found")

        feedback.is_read = feedback_update.is_read
        db.commit()
        db.refresh(feedback)
        return feedback

    @app.delete("/admin/feedback/{feedback_id}", tags=["admin"])
    def delete_feedback(
        feedback_id: int,
        current_user: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
    ):
        """Удалить отзыв"""
        db_feedback = crud.get_feedback(db=db, feedback_id=feedback_id)
        if db_feedback is None:
            raise HTTPException(status_code=404, detail="Feedback not found")
        crud.delete_feedback(db=db, feedback_id=feedback_id)
        return {"message": "Feedback deleted successfully"}

    # Campaigns
    @app.get("/admin/campaigns", response_model=List[dict], tags=["admin"])
    async def get_campaigns(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        campaigns = db.query(DonationCampaign).all()
        return [{"id": campaign.id, "title": campaign.title, "description": campaign.description, "wallet_id": campaign.wallet_id, "is_active": campaign.is_active} for campaign in campaigns]

    @app.get("/admin/campaigns/{campaign_id}", response_model=dict, tags=["admin"])
    async def get_campaign(campaign_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        campaign = db.query(DonationCampaign).filter(DonationCampaign.id == campaign_id).first()
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        return {"id": campaign.id, "title": campaign.title, "description": campaign.description, "wallet_id": campaign.wallet_id, "is_active": campaign.is_active}

    @app.post("/admin/campaigns", response_model=dict, tags=["admin"])
    async def create_campaign(campaign_data: CampaignCreate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        campaign = DonationCampaign(**campaign_data.dict())
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        return {"id": campaign.id, "title": campaign.title, "description": campaign.description, "wallet_id": campaign.wallet_id, "is_active": campaign.is_active}

    @app.put("/admin/campaigns/{campaign_id}", response_model=dict, tags=["admin"])
    async def update_campaign(campaign_id: int, campaign_data: CampaignUpdate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        campaign = db.query(DonationCampaign).filter(DonationCampaign.id == campaign_id).first()
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        for field, value in campaign_data.dict(exclude_unset=True).items():
            setattr(campaign, field, value)
        
        db.commit()
        db.refresh(campaign)
        return {"id": campaign.id, "title": campaign.title, "description": campaign.description, "wallet_id": campaign.wallet_id, "is_active": campaign.is_active}

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
        return [{"id": wallet.id, "name": wallet.name, "usdt_trc20": wallet.usdt_trc20, "eth": wallet.eth, "btc": wallet.btc} for wallet in wallets]

    @app.get("/admin/wallets/{wallet_id}", response_model=dict, tags=["admin"])
    async def get_wallet(wallet_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        return {"id": wallet.id, "name": wallet.name, "usdt_trc20": wallet.usdt_trc20, "eth": wallet.eth, "btc": wallet.btc}

    @app.post("/admin/wallets", response_model=dict, tags=["admin"])
    async def create_wallet(wallet_data: WalletCreate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        wallet = Wallet(**wallet_data.dict())
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
        return {"id": wallet.id, "name": wallet.name, "usdt_trc20": wallet.usdt_trc20, "eth": wallet.eth, "btc": wallet.btc}

    @app.put("/admin/wallets/{wallet_id}", response_model=dict, tags=["admin"])
    async def update_wallet(wallet_id: int, wallet_data: WalletUpdate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        
        for field, value in wallet_data.dict(exclude_unset=True).items():
            setattr(wallet, field, value)
        
        db.commit()
        db.refresh(wallet)
        return {"id": wallet.id, "name": wallet.name, "usdt_trc20": wallet.usdt_trc20, "eth": wallet.eth, "btc": wallet.btc}

    @app.delete("/admin/wallets/{wallet_id}", tags=["admin"])
    async def delete_wallet(wallet_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        db.delete(wallet)
        db.commit()
        return {"message": "Wallet deleted successfully"}

    # Publications
    @app.get("/admin/publications", response_model=List[dict], tags=["admin"])
    async def get_publications(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        publications = db.query(Publication).all()
        return [
            {
                "id": pub.id,
                "title": pub.title,
                "slug": pub.slug,
                "photo": pub.photo,
                "text": pub.text,
                "is_active": pub.is_active,
                "is_fundraising": pub.is_fundraising,
                "source_link": pub.source_link,
                "file_path": pub.file_path,
                "ipfs_link": pub.ipfs_link,
                "views": pub.views,
                "created_at": pub.created_at,
                "updated_at": pub.updated_at
            }
            for pub in publications
        ]

    @app.get("/admin/publications/{publication_id}", response_model=dict, tags=["admin"])
    async def get_publication(publication_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        publication = db.query(Publication).filter(Publication.id == publication_id).first()
        if not publication:
            raise HTTPException(status_code=404, detail="Publication not found")
        return {
            "id": publication.id,
            "title": publication.title,
            "slug": publication.slug,
            "photo": publication.photo,
            "text": publication.text,
            "is_active": publication.is_active,
            "is_fundraising": publication.is_fundraising,
            "source_link": publication.source_link,
            "file_path": publication.file_path,
            "ipfs_link": publication.ipfs_link,
            "views": publication.views,
            "created_at": publication.created_at,
            "updated_at": publication.updated_at,
            "status_publication": {"ipfs": "ok" if publication.ipfs_link else "fail"}
        }

    def upload_to_ipfs(filepath: str) -> str | None:
        import os
        import requests
        api_key = settings.PINATA_API_KEY
        api_secret = settings.PINATA_API_SECRET
        if not api_key or not api_secret:
            return None
        url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
        headers = {
            "pinata_api_key": api_key,
            "pinata_secret_api_key": api_secret
        }
        with open(filepath, "rb") as f:
            files = {'file': (os.path.basename(filepath), f)}
            response = requests.post(url, files=files, headers=headers)
            response.raise_for_status()
            ipfs_hash = response.json()["IpfsHash"]
            filename = os.path.basename(filepath)
            ipfs_url = f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}/{filename}"
            return ipfs_url

    @app.post("/admin/publications", response_model=dict, tags=["admin"])
    async def create_publication(
        title: str = Form(...),
        photo: UploadFile = File(None),
        text: str = Form(...),
        is_active: bool = Form(True),
        is_fundraising: bool = Form(False),
        current_admin: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
    ):
        def slugify(text):
            import re
            text = text.lower()
            text = re.sub(r'[^a-z0-9]+', '-', text)
            return text.strip('-')
        def random_link():
            import random, string
            return ''.join(random.choices(string.ascii_letters + string.digits, k=7))
        slug = slugify(title)
        source_link = random_link()
        photo_path = None
        ipfs_link = None
        if photo and getattr(photo, 'filename', None):
            if photo.filename:
                uploads_dir = "uploads/publications"
                import os
                os.makedirs(uploads_dir, exist_ok=True)
                photo_path = os.path.join(uploads_dir, photo.filename)
                contents = photo.file.read()
                with open(photo_path, "wb") as f:
                    f.write(contents)
                ipfs_link = upload_to_ipfs(photo_path)
        if db.query(Publication).filter(Publication.slug == slug).first():
            raise HTTPException(status_code=400, detail="Publication with this slug already exists")
        publication = Publication(
            title=title,
            slug=slug,
            photo=photo_path,
            text=text,
            is_active=is_active,
            is_fundraising=is_fundraising,
            source_link=source_link,
            ipfs_link=ipfs_link
        )
        db.add(publication)
        db.commit()
        db.refresh(publication)
        return {
            "id": publication.id,
            "title": publication.title,
            "slug": publication.slug,
            "photo": publication.photo,
            "text": publication.text,
            "is_active": publication.is_active,
            "is_fundraising": publication.is_fundraising,
            "source_link": publication.source_link,
            "file_path": publication.file_path,
            "ipfs_link": publication.ipfs_link,
            "views": publication.views,
            "created_at": publication.created_at,
            "updated_at": publication.updated_at,
            "status_publication": {"ipfs": "ok" if publication.ipfs_link else "fail"}
        }

    @app.put("/admin/publications/{publication_id}", response_model=dict, tags=["admin"])
    async def update_publication(
        publication_id: int,
        title: str = Form(None),
        photo: UploadFile = File(None),
        text: str = Form(None),
        is_active: bool = Form(None),
        is_fundraising: bool = Form(None),
        current_admin: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
    ):
        def slugify(text):
            import re
            text = text.lower()
            text = re.sub(r'[^a-z0-9]+', '-', text)
            return text.strip('-')
        publication = db.query(Publication).filter(Publication.id == publication_id).first()
        if not publication:
            raise HTTPException(status_code=404, detail="Publication not found")
        if title is not None:
            publication.title = title
            publication.slug = slugify(title)
        if text is not None:
            publication.text = text
        if is_active is not None:
            publication.is_active = is_active
        if is_fundraising is not None:
            publication.is_fundraising = is_fundraising
        if photo and getattr(photo, 'filename', None):
            if photo.filename:
                uploads_dir = "uploads/publications"
                import os
                os.makedirs(uploads_dir, exist_ok=True)
                photo_path = os.path.join(uploads_dir, photo.filename)
                contents = photo.file.read()
                with open(photo_path, "wb") as f:
                    f.write(contents)
                publication.photo = photo_path
                publication.ipfs_link = upload_to_ipfs(photo_path)
        db.commit()
        db.refresh(publication)
        return {
            "id": publication.id,
            "title": publication.title,
            "slug": publication.slug,
            "photo": publication.photo,
            "text": publication.text,
            "is_active": publication.is_active,
            "is_fundraising": publication.is_fundraising,
            "source_link": publication.source_link,
            "file_path": publication.file_path,
            "ipfs_link": publication.ipfs_link,
            "views": publication.views,
            "created_at": publication.created_at,
            "updated_at": publication.updated_at,
            "status_publication": {"ipfs": "ok" if publication.ipfs_link else "fail"}
        }

    @app.delete("/admin/publications/{publication_id}", tags=["admin"])
    async def delete_publication(publication_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
        publication = db.query(Publication).filter(Publication.id == publication_id).first()
        if not publication:
            raise HTTPException(status_code=404, detail="Publication not found")
        db.delete(publication)
        db.commit()
        return {"message": "Publication deleted successfully"} 