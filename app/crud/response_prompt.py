from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models
from app.schemas.response_prompt import ResponsePromptCreate


def get_response_prompts_by_id(response_prompt_id: int, db: Session):
    return (
        db.query(models.ResponsePrompt)
        .filter(models.ResponsePrompt.id == response_prompt_id)
        .all()
    )


def get_response_prompts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ResponsePrompt).offset(skip).limit(limit).all()


def create_response_prompt(response_prompt: ResponsePromptCreate, db: Session):
    try:
        db_response_prompt = models.ResponsePrompt(
            prompt_id=response_prompt.prompt_id, content_id=response_prompt.content_id
        )
        db.add(db_response_prompt)
        db.commit()
        db.refresh(db_response_prompt)
        return db_response_prompt
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
