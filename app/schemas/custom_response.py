from pydantic import BaseModel

from app.schemas.youtube_response import YoutubeVideoSimple


class CustomResponse(BaseModel):
    chatgpt: str
    contents: list[YoutubeVideoSimple]
