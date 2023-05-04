import logging
import os
import redis

from fastapi import APIRouter
from fastapi import Depends

from app import models
from app.database import SessionLocal, engine
from app.schemas.openai_response import Prompt
from app.schemas.custom_response import CustomResponse
from app.schemas.users import User
from app.schemas.youtube_response import YoutubeVideoSimple
from app.services.auth import get_current_user
from app.services.chatgpt import gpt_response
from app.services.youtube import get_credentials, fetch_videos, search_videos
from app.schemas.openai_response import Prompt

models.Base.metadata.create_all(bind=engine)

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


ACCESS_TOKEN_EXPIRE_MINUTES = float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


@router.on_event("startup")
async def startup_event():
    global cache
    pool = redis.ConnectionPool(
        host=os.getenv("REDIS_HOST"),
        port=os.getenv("REDIS_PORT"),
        db=os.getenv("REDIS_DB"),
        password=os.getenv("REDIS_PASSWORD"),
    )
    cache = redis.Redis(connection_pool=pool)


@router.post(
    "/chat",
    response_description="ChatGPT response",
    tags=["contents"],
)
async def chat(request: Prompt, current_user: User = Depends(get_current_user)):
    if cache.get(request.prompt):
        logging.info("Cache hit")
        return {"message": cache.get(request.prompt)}
    else:
        logging.info("Cache miss")
        response = gpt_response(request.prompt)
        cache.set(request.prompt, response)
        return {"message": response}


@router.post(
    "/youtube",
    response_model=list[YoutubeVideoSimple],
    response_description="Youtube videos",
    tags=["contents"],
)
async def youtube_search(
    request: Prompt, current_user: User = Depends(get_current_user)
):
    videos = search_videos(request.prompt)
    return {"content": videos}


@router.post(
    "/curious",
    response_model=CustomResponse,
    response_description="ChatGPT response and Youtube videos",
    tags=["contents"],
)
async def curious(request: Prompt, current_user: User = Depends(get_current_user)):
    if cache.get(request.prompt):
        response: str = cache.get(request.prompt)
    else:
        response: str = gpt_response(request.prompt)
        cache.set(request.prompt, response)

    credentials = await get_credentials()
    videos = fetch_videos(response, credentials)
    return {"chatgpt": response, "content": videos}


@router.on_event("shutdown")
async def shutdown_event():
    cache.close()
    logging.warning("Cache closed")
