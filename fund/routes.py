from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session

from core.database import get_db
from auth.dependencies import get_current_user
from users.models import User
from . import crud, schemas

router = APIRouter(prefix="/fund", tags=["fund"])

def get_admin_user(current_user: Annotated[User, Security(get_current_user)]):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions. Only admin can access this endpoint."
        )
    return current_user

@router.get("/info", response_model=schemas.FundInfo)
def read_fund_info(
    db: Annotated[Session, Depends(get_db)]
):
    fund_info = crud.get_fund_info(db)
    if not fund_info:
        raise HTTPException(status_code=404, detail="Fund info not found")
    return fund_info

@router.post("/info", response_model=schemas.FundInfo)
def create_fund_info(
    fund_info: schemas.FundInfoCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Security(get_admin_user)]
):
    existing_info = crud.get_fund_info(db)
    if existing_info:
        raise HTTPException(
            status_code=400,
            detail="Fund info already exists. Use PUT to update."
        )
    return crud.create_fund_info(db=db, fund_info=fund_info)

@router.put("/info", response_model=schemas.FundInfo)
def update_fund_info(
    fund_info: schemas.FundInfoUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Security(get_admin_user)]
):
    updated_info = crud.update_fund_info(db, fund_info=fund_info)
    if not updated_info:
        raise HTTPException(status_code=404, detail="Fund info not found")
    return updated_info

# Social Links
@router.post("/social-links", response_model=schemas.SocialLink)
def create_social_link(
    social_link: schemas.SocialLinkCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Security(get_admin_user)]
):
    return crud.create_social_link(db=db, social_link=social_link)

@router.get("/social-links/{fund_id}", response_model=List[schemas.SocialLink])
def read_social_links(
    fund_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    return crud.get_social_links(db=db, fund_id=fund_id)

@router.delete("/social-links/{social_link_id}")
def delete_social_link(
    social_link_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Security(get_admin_user)]
):
    if not crud.delete_social_link(db=db, social_link_id=social_link_id):
        raise HTTPException(status_code=404, detail="Social link not found")
    return {"message": "Social link deleted successfully"}

# Bank Details
@router.post("/bank-details", response_model=schemas.BankDetail)
def create_bank_detail(
    bank_detail: schemas.BankDetailCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Security(get_admin_user)]
):
    return crud.create_bank_detail(db=db, bank_detail=bank_detail)

@router.get("/bank-details/{fund_id}", response_model=List[schemas.BankDetail])
def read_bank_details(
    fund_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    return crud.get_bank_details(db=db, fund_id=fund_id)

@router.delete("/bank-details/{bank_detail_id}")
def delete_bank_detail(
    bank_detail_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Security(get_admin_user)]
):
    if not crud.delete_bank_detail(db=db, bank_detail_id=bank_detail_id):
        raise HTTPException(status_code=404, detail="Bank detail not found")
    return {"message": "Bank detail deleted successfully"} 