import json
import logging
import os
import redis

from fastapi import APIRouter
from fastapi import Depends

from app import models
from app.database import SessionLocal, engine
from sqlalchemy.orm import Session
from app.schemas.openai_response import AIResponse, Prompt, Subject
from app.schemas.contents import PromptAndContentResponse
from app.schemas.users import User
from app.schemas.youtube_response import YoutubeVideoSimple
from app.services.auth import get_current_user
from app.services.chatgpt import gpt_response, gpt_json_response
from app.services.youtube import search_videos
from app.schemas.openai_response import Prompt
from app.services.search import querySearchEngines

models.Base.metadata.create_all(bind=engine)

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
    response_model=list[PromptAndContentResponse],
    response_description="ChatGPT response and Google retrieved contents",
    tags=["contents"],
)
async def curious(
    request: Prompt,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if cache.get(request.prompt):
        logging.info("Cache hit")
        response: str = cache.get(request.prompt)
        json_dict = json.loads(response)
        ai_response = AIResponse.parse_obj(json_dict)
    else:
        logging.info("Cache miss")
        ai_response: AIResponse = gpt_json_response(request.prompt)
        json_string = ai_response.json()
        cache.set(request.prompt, str(json_string))

    all_prompt_and_response: list[PromptAndContentResponse] = []

    async def process_subjects(
        subjects: list[Subject],
        all_prompt_and_response: list[PromptAndContentResponse],
        user_id: int,
    ):
        for subject in subjects:
            prompt_and_response: PromptAndContentResponse = await querySearchEngines(
                subject.name, user_id, db
            )
            all_prompt_and_response.append(prompt_and_response)
        return all_prompt_and_response

    all_prompt_and_response = []
    all_prompt_and_response = await process_subjects(
        ai_response.basic_subjects, all_prompt_and_response, current_user.id
    )
    all_prompt_and_response = await process_subjects(
        ai_response.deeper_subjects, all_prompt_and_response, current_user.id
    )
    return all_prompt_and_response


@router.on_event("shutdown")
async def shutdown_event():
    cache.close()
    logging.warning("Cache closed")
