from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models
from app.schemas.follows import FollowCreate


def get_follows_by_user_id(user_id: int, db: Session):
    return db.query(models.Follows).filter(models.Follows.user_id == user_id).all()


def get_followers_by_user_id(user_id: int, db: Session):
    return db.query(models.Follows).filter(models.Follows.follow_id == user_id).all()


def get_follow_by_user_id_and_follow_id(user_id: int, follow_id: int, db: Session):
    follow = (
        db.query(models.Follows).filter_by(user_id=user_id, follow_id=follow_id).first()
    )

    if follow is None:
        raise HTTPException(
            status_code=404,
            detail=f"No follow found from {user_id} to {follow_id}",
        )
    return follow


def get_user_by_username(username: str, db: Session):
    return db.query(models.User).filter(models.User.username == username).first()


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
    followed_user = get_user_by_username(username, db)

    if followed_user is None:
        raise HTTPException(
            status_code=404, detail=f"User not found for username {username}"
        )

    return create_follow(FollowCreate(user_id=user_id, follow_id=followed_user.id), db)


def delete_follow(user_id: int, follow_id: int, db: Session):
    db_unfollow = (
        db.query(models.Follows).filter_by(follow_id=follow_id, user_id=user_id).first()
    )

    if db_unfollow is not None:
        db.delete(db_unfollow)
        db.commit()
        return db_unfollow
    else:
        raise HTTPException(status_code=400, detail="Unfollow failed")
