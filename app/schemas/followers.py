from pydantic import BaseModel


class FollowingBase(BaseModel):
    user_id: int
    following_id: int


class FollowingCreate(FollowingBase):
    pass


class Following(FollowingBase):
    id: int

    class Config:
        orm_mode = True
