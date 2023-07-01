from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models
from app.schemas import contents


def get_content(content_id: int, db: Session):
    return db.query(models.Content).filter(models.Content.id == content_id).first()


def get_content_by_link(link: str, db: Session):
    return db.query(models.Content).filter(models.Content.link == link).first()


def get_content_by_title(title: str, db: Session):
    return db.query(models.Content).filter(models.Content.title == title).first()


def get_contents(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Content).offset(skip).limit(limit).all()


def create_content(content: contents.ContentCreate, source: str, db: Session):
    try:
        db_content = models.Content(
            title=content.title,
            snippet=content.snippet,
            link=content.link,
            source=source,
            long_description=content.long_description,
            image=content.image,
        )
        db.add(db_content)
        db.commit()
        db.refresh(db_content)
        return db_content
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
