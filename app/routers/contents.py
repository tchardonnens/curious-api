import json
import logging
import os
import redis

from fastapi import APIRouter, HTTPException
from fastapi import Depends

from app import models
from app.crud import prompts
from app.database import SessionLocal, engine
from sqlalchemy.orm import Session
from app.schemas.llm import LLMResponse, Subject, CuriousInput
from app.schemas.contents import SubjectResources
from app.schemas.prompts import PromptCreate
from app.schemas.users import User
from app.services.auth import get_current_user
from app.services.chatgpt import gpt_json_response
from app.services.search import search_resources

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
async def chat(request: CuriousInput, current_user: User = Depends(get_current_user)):
    if cache.get(request.prompt):
        logging.info("Cache hit")
        response: str = cache.get(request)
        json_dict = json.loads(response)
        llm_answer = LLMResponse.parse_obj(json_dict)
    else:
        logging.info("Cache miss")
        llm_answer: LLMResponse = gpt_json_response(request)
        json_string = llm_answer.json()
        cache.set(request, str(json_string))

    if (
        llm_answer.basic_subjects[0].detailed_name
        or llm_answer.deeper_subjects[0].detailed_name
        or llm_answer.main_subject_of_the_prompt
    ) == "string":
        raise HTTPException(status_code=404, detail="Subject not found")
    else:
        return llm_answer.json()


@router.post(
    "/curious",
    response_model=list[SubjectResources],
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
        llm_answer = LLMResponse.parse_obj(json_dict)
    else:
        logging.info("Cache miss")
        llm_answer = gpt_json_response(request.prompt)
        json_string = llm_answer.json()
        cache.set(request.prompt, json_string)

    all_resources_for_prompt = []

    async def search_contents_for_subjects(
        prompt_in_db: models.Prompt,
        subjects: list[Subject],
        all_resources_for_prompt: list[SubjectResources],
    ):
        for subject in subjects:
            resources = await search_resources(
                prompt_in_db, subject.detailed_name, subject.description, db
            )
            all_resources_for_prompt.append(resources)
        return all_resources_for_prompt

    created_prompt = prompts.create_prompt(
        PromptCreate(
            title=request.prompt,
            keywords=llm_answer.main_subject_of_the_prompt,
            is_private=request.is_private,
            user_id=current_user.id,
        ),
        db,
    )

    if llm_answer.basic_subjects != "string":
        all_resources_for_prompt = await search_contents_for_subjects(
            created_prompt,
            llm_answer.basic_subjects,
            all_resources_for_prompt,
        )
    else:
        raise HTTPException(
            status_code=404, detail="No basic subjects found, LLM failed"
        )

    if llm_answer.deeper_subjects != "string":
        all_resources_for_prompt = await search_contents_for_subjects(
            created_prompt,
            llm_answer.deeper_subjects,
            all_resources_for_prompt,
        )
    else:
        raise HTTPException(
            status_code=404, detail="No deeper subjects found, LLM failed"
        )

    return all_resources_for_prompt


@router.on_event("shutdown")
async def shutdown_event():
    cache.close()
    logging.warning("Cache closed")
