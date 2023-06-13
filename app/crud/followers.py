from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models
from app.schemas import followers


def get_followers_by_user_id(user_id: int, db: Session):
    return db.query(models.Followers).filter(models.Followers.user_id == user_id).all()


def create_follower(follower: followers.FollowerCreate, db: Session):
    try:
        db_follower = models.Followers(
            user_id=follower.user_id,
            follower_id=follower.follower_id,
        )
        db.add(db_follower)
        db.commit()
        db.refresh(db_follower)
        return db_follower
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def delete_follower(follower_id: int, db: Session):
    try:
        db_follower = (
            db.query(models.Followers)
            .filter(models.Followers.id == follower_id)
            .first()
        )
        db.delete(db_follower)
        db.commit()
        return db_follower
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
