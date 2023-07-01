from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app import models
from app.schemas import users as user_schemas
from app.services.auth import get_password_hash


def get_user(user_id: int, db: Session):
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail=f"User not found for id {user_id}")

    return user


def get_user_by_email(email: str, db: Session):
    user = db.query(models.User).filter(models.User.email == email).first()

    if user is None:
        raise HTTPException(status_code=404, detail=f"User not found for email {email}")

    return user


def get_user_by_username(username: str, db: Session):
    user = db.query(models.User).filter(models.User.username == username).first()

    if user is None:
        raise HTTPException(
            status_code=404, detail=f"User not found for username {username}"
        )

    return user


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(user: user_schemas.UserCreate, db: Session):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        username=user.username,
        full_name=user.full_name,
    )
    db.add(db_user)

    try:
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="User already exists or invalid data."
        )

    return db_user
