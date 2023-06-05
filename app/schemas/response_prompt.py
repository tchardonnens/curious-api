from pydantic import BaseModel
from datetime import datetime


class ResponsePromptBase(BaseModel):
    prompt_id: int
    content_id: int


class ResponsePromptCreate(ResponsePromptBase):
    pass


class ResponsePrompt(ResponsePromptBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
