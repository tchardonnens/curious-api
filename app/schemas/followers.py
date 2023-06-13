from pydantic import BaseModel


class FollowerBase(BaseModel):
    user_id: int
    follower_id: int


class FollowerCreate(FollowerBase):
    pass


class Follower(FollowerBase):
    id: int

    class Config:
        orm_mode = True
