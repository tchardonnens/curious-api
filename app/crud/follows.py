from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models
from app.crud import users
from app.schemas.follows import FollowCreate


def get_follows_by_user_id(user_id: int, db: Session):
    try:
        return db.query(models.Follows).filter(models.Follows.user_id == user_id).all()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def get_followers_by_user_id(user_id: int, db: Session):
    try:
        return (
            db.query(models.Follows).filter(models.Follows.follow_id == user_id).all()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def get_follow_by_user_id_and_follow_id(user_id: int, follow_id: int, db: Session):
    try:
        return (
            db.query(models.Follows)
            .filter(models.Follows.user_id == user_id)
            .filter(models.Follows.follow_id == follow_id)
            .first()
        )
    except:
        raise HTTPException(
            status_code=400,
            detail="No follow found from {} to {}".format(user_id, follow_id),
        )


def create_follow(follow: FollowCreate, db: Session):
    try:
        db_follow = models.Follows(
            user_id=follow.user_id,
            follow_id=follow.follow_id,
        )
        db.add(db_follow)
        db.commit()
        db.refresh(db_follow)
        return db_follow
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def create_follow_by_username(username: str, user_id: int, db: Session):
    try:
        db_follow = users.get_user_by_username(username, db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    try:
        db_follow = models.Follows(
            user_id=user_id,
            follow_id=db_follow.id,
        )
        db.add(db_follow)
        db.commit()
        db.refresh(db_follow)
        return db_follow
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def delete_follow(user_id: int, follow_id: int, db: Session):
    try:
        db_unfollow = (
            db.query(models.Follows)
            .filter(
                models.Follows.follow_id == follow_id
                and models.Follows.user_id == user_id
            )
            .first()
        )
        db.delete(db_unfollow)
        db.commit()
        return db_unfollow
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
