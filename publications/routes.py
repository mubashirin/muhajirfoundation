from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from . import crud, schemas
from ..dependencies import get_db  # предположительно, как в других модулях
import os

router = APIRouter(prefix="/publications", tags=["publications"])


@router.get("/", response_model=List[schemas.PublicationOut])
def list_publications(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_publications(db, skip=skip, limit=limit)


@router.get("/{publication_id}", response_model=schemas.PublicationOut)
def get_publication(publication_id: int, db: Session = Depends(get_db)):
    publication = crud.get_publication(db, publication_id)
    if not publication:
        raise HTTPException(status_code=404, detail="Publication not found")
    return publication


@router.post("/", response_model=schemas.PublicationOut)
def create_publication(
    title: str = Form(...),
    slug: str = Form(...),
    photo: UploadFile = File(None),
    text: str = Form(...),
    is_active: bool = Form(True),
    is_fundraising: bool = Form(False),
    source_link: str = Form(None),
    file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    photo_path = None
    if photo and getattr(photo, 'filename', None):
        if photo.filename:
            uploads_dir = "uploads/publications"
            os.makedirs(uploads_dir, exist_ok=True)
            photo_path = os.path.join(uploads_dir, photo.filename)
            contents = photo.file.read()
            with open(photo_path, "wb") as f:
                f.write(contents)
    file_path = None
    if file and getattr(file, 'filename', None):
        if file.filename:
            uploads_dir = "uploads/publications"
            os.makedirs(uploads_dir, exist_ok=True)
            file_path = os.path.join(uploads_dir, file.filename)
            contents = file.file.read()
            with open(file_path, "wb") as f:
                f.write(contents)
    publication_in = schemas.PublicationCreate(
        title=title,
        slug=slug,
        photo=photo_path,
        text=text,
        is_active=is_active,
        is_fundraising=is_fundraising,
        source_link=source_link,
        file_path=file_path
    )
    return crud.create_publication(db, publication_in, file_path=file_path)


@router.put("/{publication_id}", response_model=schemas.PublicationOut)
def update_publication(publication_id: int, publication: schemas.PublicationUpdate, db: Session = Depends(get_db)):
    updated = crud.update_publication(db, publication_id, publication)
    if not updated:
        raise HTTPException(status_code=404, detail="Publication not found")
    return updated


@router.delete("/{publication_id}", response_model=dict)
def delete_publication(publication_id: int, db: Session = Depends(get_db)):
    success = crud.delete_publication(db, publication_id)
    if not success:
        raise HTTPException(status_code=404, detail="Publication not found")
    return {"ok": True} 