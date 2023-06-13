from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models
from app.schemas import followings


def get_followings_by_user_id(user_id: int, db: Session):
    return (
        db.query(models.Followings).filter(models.Followings.user_id == user_id).all()
    )


def create_following(following: followings.FollowingCreate, db: Session):
    try:
        db_following = models.Followings(
            user_id=following.user_id,
            following_id=following.following_id,
        )
        db.add(db_following)
        db.commit()
        db.refresh(db_following)
        return db_following
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def delete_following(following_id: int, db: Session):
    try:
        db_following = (
            db.query(models.Followings)
            .filter(models.Followings.id == following_id)
            .first()
        )
        db.delete(db_following)
        db.commit()
        return db_following
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
