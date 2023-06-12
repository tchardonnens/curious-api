from pydantic import BaseModel
from .prompts import Prompt


class ContentBase(BaseModel):
    title: str
    snippet: str
    link: str
    source: str
    long_description: str
    image: str


class ContentCreate(ContentBase):
    pass


class Content(ContentBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True


class AllSourcesContent(BaseModel):
    youtube: list[Content]
    reddit: list[Content]
    twitter: list[Content]


class SubjectAndContents(BaseModel):
    subject: Prompt
    content: AllSourcesContent
