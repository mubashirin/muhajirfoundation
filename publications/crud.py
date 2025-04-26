from sqlalchemy.orm import Session
from .models import Publication
from .schemas import PublicationCreate, PublicationUpdate
from typing import List, Optional


def get_publication(db: Session, publication_id: int) -> Optional[Publication]:
    pub = db.query(Publication).filter(Publication.id == publication_id).first()
    if pub:
        for field in ['photo', 'file_path']:
            value = getattr(pub, field)
            if isinstance(value, bytes):
                print(f"{field} type: bytes, len: {len(value)}")
            else:
                print(f"{field} type: {type(value)}, value: {str(value)[:40]}")
    return pub


def get_publications(db: Session, skip: int = 0, limit: int = 100) -> List[Publication]:
    pubs = db.query(Publication).offset(skip).limit(limit).all()
    for pub in pubs:
        for field in ['photo', 'file_path']:
            value = getattr(pub, field)
            if isinstance(value, bytes):
                print(f"{field} type: bytes, len: {len(value)}")
            else:
                print(f"{field} type: {type(value)}, value: {str(value)[:40]}")
    return pubs


def create_publication(db: Session, publication: PublicationCreate, file_path: str = None) -> Publication:
    data = publication.dict()
    if file_path is not None:
        data["file_path"] = file_path
    db_publication = Publication(**data)
    db.add(db_publication)
    db.commit()
    db.refresh(db_publication)
    return db_publication


def update_publication(db: Session, publication_id: int, publication: PublicationUpdate) -> Optional[Publication]:
    db_publication = get_publication(db, publication_id)
    if not db_publication:
        return None
    for field, value in publication.dict(exclude_unset=True).items():
        setattr(db_publication, field, value)
    db.commit()
    db.refresh(db_publication)
    return db_publication


def delete_publication(db: Session, publication_id: int) -> bool:
    db_publication = get_publication(db, publication_id)
    if not db_publication:
        return False
    db.delete(db_publication)
    db.commit()
    return True 