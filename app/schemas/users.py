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
    bio: str
    profile_picture: str
    profile_banner: str

    class Config:
        orm_mode = True


class UserWithSocialNetwork(User):
    followers: list[int]
    followings: list[int]
