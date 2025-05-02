from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from users.models import User
from fund.models import FundInfo, SocialLink, BankDetail
from fund.schemas import FundInfoCreate, FundInfoUpdate, FundInfoResponse
from admin.deps import get_current_admin
from admin.crud import BaseCRUD

router = APIRouter(prefix="/admin/fund", tags=["admin-fund"])

fund_crud = BaseCRUD(FundInfo)
social_link_crud = BaseCRUD(SocialLink)
bank_detail_crud = BaseCRUD(BankDetail)

# Fund Info
@router.get("/info", response_model=List[FundInfoResponse])
async def get_fund_info(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    return fund_crud.get_multi(db, skip=skip, limit=limit)

@router.get("/info/{fund_id}", response_model=FundInfoResponse)
async def get_fund_info_item(
    fund_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    fund_info = fund_crud.get(db, id=fund_id)
    if not fund_info:
        raise HTTPException(status_code=404, detail="Fund info not found")
    return fund_info

@router.post("/info", response_model=FundInfoResponse)
async def create_fund_info(
    fund_info_in: FundInfoCreate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return fund_crud.create(db, obj_in=fund_info_in)

@router.put("/info/{fund_id}", response_model=FundInfoResponse)
async def update_fund_info(
    fund_id: int,
    fund_info_in: FundInfoUpdate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    fund_info = fund_crud.get(db, id=fund_id)
    if not fund_info:
        raise HTTPException(status_code=404, detail="Fund info not found")
    return fund_crud.update(db, db_obj=fund_info, obj_in=fund_info_in)

@router.delete("/info/{fund_id}")
async def delete_fund_info(
    fund_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    fund_info = fund_crud.get(db, id=fund_id)
    if not fund_info:
        raise HTTPException(status_code=404, detail="Fund info not found")
    fund_crud.remove(db, id=fund_id)
    return {"message": "Fund info deleted successfully"}

# Social Links
@router.get("/social-links", response_model=List[dict])
async def get_social_links(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    return social_link_crud.get_multi(db, skip=skip, limit=limit)

@router.post("/social-links", response_model=dict)
async def create_social_link(
    link_data: dict,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return social_link_crud.create(db, obj_in=link_data)

@router.put("/social-links/{link_id}", response_model=dict)
async def update_social_link(
    link_id: int,
    link_data: dict,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    link = social_link_crud.get(db, id=link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Social link not found")
    return social_link_crud.update(db, db_obj=link, obj_in=link_data)

@router.delete("/social-links/{link_id}")
async def delete_social_link(
    link_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    link = social_link_crud.get(db, id=link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Social link not found")
    social_link_crud.remove(db, id=link_id)
    return {"message": "Social link deleted successfully"}

# Bank Details
@router.get("/bank-details", response_model=List[dict])
async def get_bank_details(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    return bank_detail_crud.get_multi(db, skip=skip, limit=limit)

@router.post("/bank-details", response_model=dict)
async def create_bank_detail(
    detail_data: dict,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return bank_detail_crud.create(db, obj_in=detail_data)

@router.put("/bank-details/{detail_id}", response_model=dict)
async def update_bank_detail(
    detail_id: int,
    detail_data: dict,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    detail = bank_detail_crud.get(db, id=detail_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Bank detail not found")
    return bank_detail_crud.update(db, db_obj=detail, obj_in=detail_data)

@router.delete("/bank-details/{detail_id}")
async def delete_bank_detail(
    detail_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    detail = bank_detail_crud.get(db, id=detail_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Bank detail not found")
    bank_detail_crud.remove(db, id=detail_id)
    return {"message": "Bank detail deleted successfully"} 