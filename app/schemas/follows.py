from pydantic import BaseModel


class FollowBase(BaseModel):
    user_id: int
    follow_id: int


class FollowCreate(FollowBase):
    pass


class Follow(FollowBase):
    id: int

    class Config:
        orm_mode = True
