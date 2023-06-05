from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models
from app.crud.response_prompt import get_response_prompts_by_id
from app.schemas import prompts
from app.crud import users


def get_prompt(prompt_id: int, db: Session):
    return db.query(models.Prompt).filter(models.Prompt.id == prompt_id).first()


def get_prompt_by_title(title: str, db: Session):
    return db.query(models.Prompt).filter(models.Prompt.title == title).first()


def get_prompts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Prompt).offset(skip).limit(limit).all()


def create_prompt(prompt: prompts.PromptCreate, db: Session):
    db_prompt = get_prompt_by_title(title=prompt.title, db=db)
    # if db_prompt:
    #     raise HTTPException(status_code=400, detail="Prompt already exists.")
    db_user = users.get_user(prompt.user_id, db)
    if db_user is None:
        raise HTTPException(status_code=400, detail="Invalid user ID.")
    try:
        db_prompt = models.Prompt(title=prompt.title, user_id=prompt.user_id)
        db.add(db_prompt)
        db.commit()
        db.refresh(db_prompt)
        return db_prompt
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def get_prompt_contents(prompt_id: int, db: Session):
    db_prompt = get_prompt(prompt_id, db)
    if db_prompt is None:
        raise HTTPException(status_code=400, detail="Prompt not found.")
    db_response_prompts = get_response_prompts_by_id(prompt_id, db)
    if db_response_prompts is None:
        raise HTTPException(status_code=400, detail="No response prompts found.")
    db_contents = []
    for db_response_prompt in db_response_prompts:
        db_content = (
            db.query(models.Content)
            .filter(models.Content.id == db_response_prompt.content_id)
            .first()
        )
        if db_content is not None:
            db_contents.append(db_content)
