from sqladmin import ModelView, Admin
from users.models import User
from fund.models import FundInfo, SocialLink, BankDetail
from feedback.models import Feedback

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

def setup_admin(app, engine):
    admin = Admin(app, engine)
    
    admin.add_view(UserAdmin)
    admin.add_view(FundInfoAdmin)
    admin.add_view(SocialLinkAdmin)
    admin.add_view(BankDetailAdmin)
    admin.add_view(FeedbackAdmin)
    
    return admin 