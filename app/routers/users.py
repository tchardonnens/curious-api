import os
from fastapi import APIRouter
from datetime import timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app import models
from app.database import SessionLocal, engine
from sqlalchemy.orm import Session

from app.schemas.auth import Token
from app.schemas.follows import Follow
from app.schemas.users import User, UserCreate, UserWithSocialNetwork
from app.services.auth import authenticate_user, create_access_token, get_current_user
from app.crud import follows, users

models.Base.metadata.create_all(bind=engine)

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


ACCESS_TOKEN_EXPIRE_MINUTES = float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


@router.post(
    "/users",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    tags=["users"],
)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return users.create_user(user, db)


@router.post("/token", response_model=Token, tags=["users"])
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/all", response_model=list[User], tags=["users"])
async def read_users(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return users.get_users(db)


@router.get(
    "/users/id/{id}", response_model=User, tags=["users"], name="Get User By ID"
)
async def read_user(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return users.get_user(id, db)


@router.get(
    "/users/mail/{email}", response_model=User, tags=["users"], name="Get User By Email"
)
async def read_user(
    email: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return users.get_user_by_email(email, db)


@router.get(
    "/users/username/{username}",
    response_model=User,
    tags=["users"],
    name="Get User By Username",
)
async def read_user(
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return users.get_user_by_username(username, db)


@router.get(
    "/users/me",
    response_model=UserWithSocialNetwork,
    tags=["users"],
    name="Get Current User",
)
async def read_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return UserWithSocialNetwork(
        user=current_user,
        follows=len(follows.get_follows_by_user_id(current_user.id, db)),
        followers=len(follows.get_followers_by_user_id(current_user.id, db)),
    )


@router.post(
    "/users/follow/username/{follow_username}",
    response_model=Follow,
    tags=["users"],
    name="Follow User",
)
async def follow_user(
    follow_username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if follow_username == current_user.username:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    followed_user = users.get_user_by_username(follow_username, db)
    follow_exists = follows.get_follow_by_user_id_and_follow_id(
        current_user.id, followed_user.id, db
    )
    if follow_exists != None:
        raise HTTPException(status_code=409, detail="Follow already exists")
    follow = follows.create_follow_by_username(
        follow_username,
        current_user.id,
        db,
    )
    return follow


@router.delete(
    "/users/follow/{follow_id}",
    tags=["users"],
    name="Unfollow User",
)
async def unfollow_user(
    follow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    follows.delete_follow(current_user.id, follow_id, db)
    return {"message": "Unfollowed successfully user_id: {}".format(follow_id)}


@router.get(
    "/users/follows/me",
    response_model=list[User],
    tags=["users"],
    name="Get follows",
)
async def get_follows(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    follow_list = follows.get_follows_by_user_id(current_user.id, db)
    return [users.get_user(follow.follow_id, db) for follow in follow_list]


@router.get(
    "/users/follows/id/{user_id}",
    response_model=list[User],
    tags=["users"],
    name="Get follows",
)
async def get_follows(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    follow_list = follows.get_follows_by_user_id(user_id, db)
    return [users.get_user(follow.follow_id, db) for follow in follow_list]


@router.get(
    "/users/followers/me",
    response_model=list[User],
    tags=["users"],
    name="Get followers",
)
async def get_followers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    follower_list = follows.get_followers_by_user_id(current_user.id, db)
    return [users.get_user(follower.user_id, db) for follower in follower_list]


@router.get(
    "/users/followers/id/{user_id}",
    response_model=list[User],
    tags=["users"],
    name="Get followers",
)
async def get_followers(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    follower_list = follows.get_followers_by_user_id(user_id, db)
    return [users.get_user(follower.user_id, db) for follower in follower_list]
