from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models
from app.schemas import users
from passlib.context import CryptContext

from app.services.auth import get_password_hash

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user(user_id: int, db: Session):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(email: str, db: Session):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_username(username: str, db: Session):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(user: users.UserCreate, db: Session):
    try:
        hashed_password = get_password_hash(user.password)
        db_user = models.User(
            email=user.email,
            hashed_password=hashed_password,
            username=user.username,
            full_name=user.full_name,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
