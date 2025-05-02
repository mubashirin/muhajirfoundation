from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import shutil
import os
from pathlib import Path

from core.database import get_db
from users.models import User
from publications.models import Publication, PublicationImage, PublicationVideo
from publications.schemas import PublicationCreate, PublicationUpdate, PublicationResponse
from admin.deps import get_current_admin
from admin.crud import BaseCRUD
from core.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/admin/publications", tags=["admin-publications"])

publication_crud = BaseCRUD(Publication)
image_crud = BaseCRUD(PublicationImage)
video_crud = BaseCRUD(PublicationVideo)

# Publications
@router.get("/", response_model=List[PublicationResponse])
async def get_publications(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    return publication_crud.get_multi(db, skip=skip, limit=limit)

@router.get("/{publication_id}", response_model=PublicationResponse)
async def get_publication(
    publication_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    publication = publication_crud.get(db, id=publication_id)
    if not publication:
        raise HTTPException(status_code=404, detail="Publication not found")
    return publication

@router.post("/", response_model=PublicationResponse)
async def create_publication(
    publication_in: PublicationCreate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return publication_crud.create(db, obj_in=publication_in)

@router.put("/{publication_id}", response_model=PublicationResponse)
async def update_publication(
    publication_id: int,
    publication_in: PublicationUpdate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    publication = publication_crud.get(db, id=publication_id)
    if not publication:
        raise HTTPException(status_code=404, detail="Publication not found")
    return publication_crud.update(db, db_obj=publication, obj_in=publication_in)

@router.delete("/{publication_id}")
async def delete_publication(
    publication_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    publication = publication_crud.get(db, id=publication_id)
    if not publication:
        raise HTTPException(status_code=404, detail="Publication not found")
    publication_crud.remove(db, id=publication_id)
    return {"message": "Publication deleted successfully"}

# Images
@router.post("/{publication_id}/images")
async def upload_image(
    publication_id: int,
    file: UploadFile = File(...),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    publication = publication_crud.get(db, id=publication_id)
    if not publication:
        raise HTTPException(status_code=404, detail="Publication not found")

    upload_dir = Path(settings.UPLOAD_DIR) / "publications" / str(publication_id) / "images"
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / file.filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    image = PublicationImage(
        publication_id=publication_id,
        path=str(file_path.relative_to(settings.UPLOAD_DIR))
    )
    db.add(image)
    db.commit()
    db.refresh(image)
    return {"message": "Image uploaded successfully", "image_id": image.id}

@router.delete("/images/{image_id}")
async def delete_image(
    image_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    image = image_crud.get(db, id=image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    file_path = Path(settings.UPLOAD_DIR) / image.path
    if file_path.exists():
        file_path.unlink()
    
    image_crud.remove(db, id=image_id)
    return {"message": "Image deleted successfully"}

# Videos
@router.post("/{publication_id}/videos")
async def upload_video(
    publication_id: int,
    file: UploadFile = File(...),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    publication = publication_crud.get(db, id=publication_id)
    if not publication:
        raise HTTPException(status_code=404, detail="Publication not found")

    upload_dir = Path(settings.UPLOAD_DIR) / "publications" / str(publication_id) / "videos"
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / file.filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    video = PublicationVideo(
        publication_id=publication_id,
        path=str(file_path.relative_to(settings.UPLOAD_DIR))
    )
    db.add(video)
    db.commit()
    db.refresh(video)
    return {"message": "Video uploaded successfully", "video_id": video.id}

@router.delete("/videos/{video_id}")
async def delete_video(
    video_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    video = video_crud.get(db, id=video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    file_path = Path(settings.UPLOAD_DIR) / video.path
    if file_path.exists():
        file_path.unlink()
    
    video_crud.remove(db, id=video_id)
    return {"message": "Video deleted successfully"} 