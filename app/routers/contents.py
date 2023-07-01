import json
import logging
import os
from pydantic import BaseModel
import redis

from fastapi import APIRouter, HTTPException
from fastapi import Depends

from app import models
from app.crud import prompts
from app.database import SessionLocal, engine
from sqlalchemy.orm import Session
from app.schemas.openai_response import AIResponse, AIPrompt, Subject
from app.schemas.contents import PromptSubjectAndContents
from app.schemas.prompts import PromptCreate, Prompt
from app.schemas.users import User
from app.services.auth import get_current_user
from app.services.chatgpt import gpt_json_response
from app.services.search import AIResponseSubjectSearchEngines

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


class CuriousInput(BaseModel):
    prompt: str
    is_private: bool


@router.post(
    "/chat",
    response_description="ChatGPT response",
    tags=["contents"],
)
async def chat(request: CuriousInput, current_user: User = Depends(get_current_user)):
    if cache.get(request.prompt):
        logging.info("Cache hit")
        response: str = cache.get(request)
        json_dict = json.loads(response)
        ai_response = AIResponse.parse_obj(json_dict)
    else:
        logging.info("Cache miss")
        ai_response: AIResponse = gpt_json_response(request)
        json_string = ai_response.json()
        cache.set(request, str(json_string))

    if (
        ai_response.basic_subjects[0].detailed_name
        or ai_response.deeper_subjects[0].detailed_name
        or ai_response.main_subject_of_the_prompt
    ) == "string":
        raise HTTPException(status_code=404, detail="Subject not found")
    else:
        return ai_response.json()


@router.post(
    "/curious",
    response_model=list[PromptSubjectAndContents],
    response_description="ChatGPT response and Google retrieved contents",
    tags=["contents"],
)
async def curious(
    request: CuriousInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cached_response = cache.get(request.prompt)

    if cached_response:
        logging.info("Cache hit")
        json_dict = json.loads(cached_response)
        ai_response = AIResponse.parse_obj(json_dict)
    else:
        logging.info("Cache miss")
        ai_response = gpt_json_response(request.prompt)
        json_string = ai_response.json()
        cache.set(request.prompt, json_string)

    all_prompt_subjects_and_contents = []

    async def process_subjects(
        prompt: str,
        subjects: list[Subject],
        all_prompt_subjects_and_contents: list[PromptSubjectAndContents],
    ):
        for subject in subjects:
            prompt_subject_and_contents = await AIResponseSubjectSearchEngines(
                prompt, subject.detailed_name, db
            )
            all_prompt_subjects_and_contents.append(prompt_subject_and_contents)
        return all_prompt_subjects_and_contents

    created_prompt = prompts.create_prompt(
        PromptCreate(
            title=request.prompt,
            keywords=ai_response.main_subject_of_the_prompt,
            is_private=request.is_private,
            user_id=current_user.id,
        ),
        db,
    )

    if ai_response.basic_subjects != "string":
        all_prompt_subjects_and_contents = await process_subjects(
            created_prompt,
            ai_response.basic_subjects,
            all_prompt_subjects_and_contents,
        )
    else:
        raise HTTPException(
            status_code=404, detail="No basic subjects found, LLM failed"
        )

    if ai_response.deeper_subjects != "string":
        all_prompt_subjects_and_contents = await process_subjects(
            created_prompt,
            ai_response.deeper_subjects,
            all_prompt_subjects_and_contents,
        )
    else:
        raise HTTPException(
            status_code=404, detail="No deeper subjects found, LLM failed"
        )

    return all_prompt_subjects_and_contents


@router.on_event("shutdown")
async def shutdown_event():
    cache.close()
    logging.warning("Cache closed")
