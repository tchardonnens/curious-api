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
from app.schemas.users import User, UserCreate
from app.services.auth import authenticate_user, create_access_token, get_current_user
from app.crud import users

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


@router.get("/users", response_model=list[User], tags=["users"])
async def read_users(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return users.get_users(db)


@router.get("/users/{id}", response_model=User, tags=["users"], name="Get User By ID")
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
