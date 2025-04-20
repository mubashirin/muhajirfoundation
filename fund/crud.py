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