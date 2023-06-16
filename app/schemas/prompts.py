from pydantic import BaseModel
from datetime import datetime


class PromptBase(BaseModel):
    title: str
    keywords: str
    user_id: int


class PromptCreate(PromptBase):
    pass


class Prompt(PromptBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
