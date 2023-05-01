from pydantic import BaseModel


class UserBase(BaseModel):
    email: str
    username: str
    full_name: str


class UserCreate(UserBase):
    password: str


class UserInDB(UserBase):
    hashed_password: str


class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True
