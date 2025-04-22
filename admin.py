from sqladmin import ModelView, Admin
from sqladmin.authentication import AuthenticationBackend
from fastapi import Request
from users.models import User
from fund.models import FundInfo, SocialLink, BankDetail
from feedback.models import Feedback
from donations.models import DonationCampaign, Wallet
from core.database import SessionLocal
from users.crud import get_user_by_email
from core.security import verify_password
from sqlalchemy.orm import joinedload
import secrets

SECRET_KEY = secrets.token_urlsafe(32)

class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]
        
        print(f"Login attempt: {username}")
        
        db = SessionLocal()
        try:
            user = get_user_by_email(db, email=username)
            
            if not user or not verify_password(password, user.hashed_password) or not user.is_superuser:
                print(f"Login failed for {username}")
                return False
                
            request.session.update({"authenticated": True, "user_id": user.id})
            print(f"Login successful for {username}")
            return True
        finally:
            db.close()

    async def logout(self, request: Request) -> bool:
        print("Logout called")
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        authenticated = request.session.get("authenticated", False)
        
        print(f"Authentication check: {authenticated}")
        
        if not authenticated:
            return False
        return True

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email, User.is_superuser, User.is_active, User.created_at]
    column_searchable_list = [User.email]
    column_sortable_list = [User.id, User.email, User.created_at]
    column_default_sort = ("id", True)
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-users"

class FundInfoAdmin(ModelView, model=FundInfo):
    column_list = [
        FundInfo.id, 
        FundInfo.name, 
        FundInfo.email, 
        FundInfo.phone,
        FundInfo.is_active,
        "social_links",
        "bank_details",
        FundInfo.created_at
    ]
    column_searchable_list = [FundInfo.name, FundInfo.email]
    column_sortable_list = [FundInfo.id, FundInfo.name, FundInfo.created_at]
    column_default_sort = ("id", True)
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    name = "Fund Info"
    name_plural = "Fund Info"
    icon = "fa-solid fa-building"
    
    column_formatters = {
        "social_links": lambda m, a: ", ".join([f"{link.platform}: {link.url}" for link in m.social_links]) if m.social_links else "No social links",
        "bank_details": lambda m, a: ", ".join([f"{bank.bank_name} ({bank.currency})" for bank in m.bank_details]) if m.bank_details else "No bank details"
    }

    def __str__(self):
        return self.name

class SocialLinkAdmin(ModelView, model=SocialLink):
    column_list = [
        SocialLink.id,
        "fund",
        SocialLink.platform,
        SocialLink.url,
        SocialLink.created_at
    ]
    column_searchable_list = [SocialLink.platform, SocialLink.url]
    column_sortable_list = [SocialLink.id, SocialLink.platform]
    column_default_sort = ("id", True)
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    name = "Social Link"
    name_plural = "Social Links"
    icon = "fa-solid fa-share-nodes"
    
    column_formatters = {
        "fund": lambda m, a: str(m.fund) if m.fund else "No fund"
    }

    def __str__(self):
        return f"{self.platform}: {self.url}"

class BankDetailAdmin(ModelView, model=BankDetail):
    column_list = [
        BankDetail.id,
        "fund",
        BankDetail.bank_name,
        BankDetail.account_number,
        BankDetail.currency,
        BankDetail.created_at
    ]
    column_searchable_list = [BankDetail.bank_name, BankDetail.account_number]
    column_sortable_list = [BankDetail.id, BankDetail.bank_name]
    column_default_sort = ("id", True)
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    name = "Bank Detail"
    name_plural = "Bank Details"
    icon = "fa-solid fa-building-columns"
    
    column_formatters = {
        "fund": lambda m, a: str(m.fund) if m.fund else "No fund"
    }

    def __str__(self):
        return f"{self.bank_name} ({self.currency})"

class FeedbackAdmin(ModelView, model=Feedback):
    column_list = [
        Feedback.id,
        Feedback.name,
        Feedback.email,
        Feedback.message,
        Feedback.is_read,
        Feedback.created_at
    ]
    column_searchable_list = [Feedback.name, Feedback.email]
    column_sortable_list = [Feedback.id, Feedback.created_at]
    column_default_sort = ("created_at", True)
    can_create = False
    can_edit = True
    can_delete = True
    can_view_details = True
    name = "Feedback"
    name_plural = "Feedback"
    icon = "fa-solid fa-message"

class DonationCampaignAdmin(ModelView, model=DonationCampaign):
    column_list = [
        DonationCampaign.id,
        DonationCampaign.uuid,
        DonationCampaign.title,
        DonationCampaign.description,
        DonationCampaign.is_active,
        "wallets",
        DonationCampaign.created_at,
        DonationCampaign.updated_at
    ]
    column_searchable_list = [DonationCampaign.title]
    column_sortable_list = [DonationCampaign.id, DonationCampaign.title, DonationCampaign.created_at]
    column_default_sort = ("created_at", True)
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    name = "Donation Campaign"
    name_plural = "Donation Campaigns"
    icon = "fa-solid fa-hand-holding-dollar"
    
    def get_list_query(self):
        return self.model.query.options(joinedload(DonationCampaign.wallets))
    
    def get_details_query(self):
        return self.model.query.options(joinedload(DonationCampaign.wallets))
    
    column_formatters = {
        "wallets": lambda m, a: ", ".join([f"{wallet.name}" for wallet in m.wallets]) if m.wallets else "No wallets"
    }

class WalletAdmin(ModelView, model=Wallet):
    column_list = [
        Wallet.id,
        Wallet.uuid,
        Wallet.name,
        "campaign",
        Wallet.usdt_trc20,
        Wallet.bch,
        Wallet.eth,
        Wallet.btc,
        Wallet.created_at,
        Wallet.updated_at
    ]
    column_searchable_list = [Wallet.name]
    column_sortable_list = [Wallet.id, Wallet.name, Wallet.created_at]
    column_default_sort = ("created_at", True)
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    name = "Wallet"
    name_plural = "Wallets"
    icon = "fa-solid fa-wallet"
    
    def get_list_query(self):
        return self.model.query.options(joinedload(Wallet.campaign))
    
    def get_details_query(self):
        return self.model.query.options(joinedload(Wallet.campaign))
    
    column_formatters = {
        "campaign": lambda m, a: m.campaign.title if m.campaign else "No campaign"
    }

def setup_admin(app, engine):
    from starlette.middleware.sessions import SessionMiddleware
    app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
    authentication_backend = AdminAuth(secret_key=SECRET_KEY)

    admin = Admin(
        app,
        engine,
        title="Muhajir Foundation Admin",
        logo_url="https://preview.tabler.io/static/logo.svg",
        authentication_backend=authentication_backend
    )
    
    admin.add_view(UserAdmin)
    admin.add_view(FundInfoAdmin)
    admin.add_view(SocialLinkAdmin)
    admin.add_view(BankDetailAdmin)
    admin.add_view(FeedbackAdmin)
    admin.add_view(DonationCampaignAdmin)
    admin.add_view(WalletAdmin)
    
    # Убираем донаты из Default
    admin.menu = [
        {"name": "Users", "icon": "fa-solid fa-users", "models": [UserAdmin]},
        {"name": "Fund Info", "icon": "fa-solid fa-building", "models": [FundInfoAdmin, SocialLinkAdmin, BankDetailAdmin]},
        {"name": "Feedback", "icon": "fa-solid fa-message", "models": [FeedbackAdmin]},
        {"name": "Donations", "icon": "fa-solid fa-hand-holding-dollar", "models": [DonationCampaignAdmin, WalletAdmin]}
    ]
    
    return admin 