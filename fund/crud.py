from sqlalchemy.orm import Session
from . import models, schemas

def get_fund_info(db: Session):
    return db.query(models.FundInfo).first()

def create_fund_info(db: Session, fund_info: schemas.FundInfoCreate):
    db_fund_info = models.FundInfo(**fund_info.model_dump())
    db.add(db_fund_info)
    db.commit()
    db.refresh(db_fund_info)
    return db_fund_info

def update_fund_info(db: Session, fund_info: schemas.FundInfoUpdate):
    db_fund_info = get_fund_info(db)
    if not db_fund_info:
        return None
    
    update_data = fund_info.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_fund_info, field, value)
    
    db.commit()
    db.refresh(db_fund_info)
    return db_fund_info

def create_social_link(db: Session, social_link: schemas.SocialLinkCreate):
    db_social_link = models.SocialLink(**social_link.model_dump())
    db.add(db_social_link)
    db.commit()
    db.refresh(db_social_link)
    return db_social_link

def get_social_links(db: Session, fund_id: int):
    return db.query(models.SocialLink).filter(models.SocialLink.fund_id == fund_id).all()

def delete_social_link(db: Session, social_link_id: int):
    db_social_link = db.query(models.SocialLink).filter(models.SocialLink.id == social_link_id).first()
    if db_social_link:
        db.delete(db_social_link)
        db.commit()
        return True
    return False

def create_bank_detail(db: Session, bank_detail: schemas.BankDetailCreate):
    db_bank_detail = models.BankDetail(**bank_detail.model_dump())
    db.add(db_bank_detail)
    db.commit()
    db.refresh(db_bank_detail)
    return db_bank_detail

def get_bank_details(db: Session, fund_id: int):
    return db.query(models.BankDetail).filter(models.BankDetail.fund_id == fund_id).all()

def delete_bank_detail(db: Session, bank_detail_id: int):
    db_bank_detail = db.query(models.BankDetail).filter(models.BankDetail.id == bank_detail_id).first()
    if db_bank_detail:
        db.delete(db_bank_detail)
        db.commit()
        return True
    return False 