from pydantic import BaseModel


class CleanGoogleResult(BaseModel):
    title: str
    snippet: str
    link: str
    long_description: str
    image: str


class AllSourcesCleanGoogleResult(BaseModel):
    youtube: list[CleanGoogleResult]
    reddit: list[CleanGoogleResult]
    twitter: list[CleanGoogleResult]


class CustomResponse(BaseModel):
    chatgpt: str
    content: AllSourcesCleanGoogleResult
