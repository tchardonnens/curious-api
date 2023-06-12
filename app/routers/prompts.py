import os
from fastapi import APIRouter, Depends
import redis
from requests import Session

from app import models
from app.crud import prompts
from app.database import SessionLocal, engine
from app.schemas.contents import Content, PromptSubjectAndContents
from app.schemas.prompts import PromptBase, Prompt
from app.schemas.users import User
from app.services.auth import get_current_user

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


@router.get("/prompts/me", response_model=list[Prompt], tags=["prompts"])
async def get_prompts(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return prompts.get_prompts_by_user_id(current_user.id, db)


@router.get(
    "/prompts/profile/me",
    response_model=list[PromptSubjectAndContents],
    tags=["prompts"],
)
async def get_prompts(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    list_of_prompts = prompts.get_last_three_prompts_by_user_id(current_user.id, db)
    list_of_contents = []
    for prompt in list_of_prompts:
        content_for_prompt = prompts.get_prompt_contents(prompt.id, db)
        list_of_contents.append(content_for_prompt)
    return list_of_contents


@router.get("/prompts/{prompt_id}", response_model=Prompt, tags=["prompts"])
async def get_prompt_by_id(
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return prompts.get_prompt_by_id(prompt_id, db)


@router.post("/prompts", response_model=Prompt, tags=["prompts"])
async def create_prompt(
    request: PromptBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return prompts.create_prompt(request, db)


@router.get(
    "/prompts/{prompt_id}/contents", response_model=list[Content], tags=["prompts"]
)
async def get_prompt_contents(
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return prompts.get_prompt_contents(prompt_id, db)
