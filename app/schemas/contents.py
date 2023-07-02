from pydantic import BaseModel

from .prompts import Prompt
from .users import User


class ContentBase(BaseModel):
    title: str
    snippet: str
    link: str
    long_description: str
    image: str


class ContentCreate(ContentBase):
    source: str


class Content(ContentBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True


class SubjectResources(BaseModel):
    prompt: Prompt
    subject: str
    description: str
    contents: list[Content]


class UserSubjectResources(SubjectResources):
    user: User
