import logging
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models
from app.crud import contents
from app.crud.contents import get_contents
from app.crud.response_prompt import (
    get_content_ids_by_ai_response_subject,
    get_response_prompts_by_id,
    get_three_response_prompts_by_id,
)
from app.schemas import prompts
from app.crud import users
from app.schemas.contents import PromptSubjectAndContents, UserPromptSubjectAndContents


def get_prompt_by_id(prompt_id: int, db: Session):
    return db.query(models.Prompt).filter(models.Prompt.id == prompt_id).first()


def get_prompt_by_title(title: str, db: Session):
    return db.query(models.Prompt).filter(models.Prompt.title == title).first()


def get_prompts_by_user_id(user_id: int, db: Session):
    return db.query(models.Prompt).filter(models.Prompt.user_id == user_id).all()


def get_last_three_prompts_by_user_id(user_id: int, db: Session):
    return db.query(models.Prompt).filter(models.Prompt.user_id == user_id).all()[-3:]


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


def get_prompt_contents(prompt_id: int, db: Session) -> UserPromptSubjectAndContents:
    db_prompt = get_prompt_by_id(prompt_id, db)
    if db_prompt is None:
        raise HTTPException(status_code=400, detail="Prompt not found.")
    db_user = users.get_user(db_prompt.user_id, db)
    if db_user is None:
        raise HTTPException(status_code=400, detail="User not found.")
    db_response_prompts = get_three_response_prompts_by_id(prompt_id, db)
    if db_response_prompts is None:
        raise HTTPException(status_code=400, detail="No response prompts found.")
    db_contents = []
    for db_response_prompt in db_response_prompts:
        db_contents.append(contents.get_content(db_response_prompt.content_id, db))

    return UserPromptSubjectAndContents(
        user=db_user,
        prompt=db_prompt,
        subject=db_response_prompt.ai_response_subject,
        contents=db_contents,
    )


def get_prompt_contents_history(
    prompt_id: int, db: Session
) -> list[PromptSubjectAndContents]:
    db_prompt = get_prompt_by_id(prompt_id, db)
    if db_prompt is None:
        raise HTTPException(status_code=400, detail="Prompt not found.")
    db_response_prompts = get_response_prompts_by_id(prompt_id, db)
    if db_response_prompts is None:
        raise HTTPException(status_code=400, detail="No response prompts found.")

    # Keep track of subjects and their associated contents
    subject_contents_map = {}

    # Keep track of content_ids that have been processed
    processed_content_ids = set()

    for db_response_prompt in db_response_prompts:
        subject = db_response_prompt.ai_response_subject
        # Initialize the subject key if not already present
        if subject not in subject_contents_map:
            subject_contents_map[subject] = []

        # Fetch content_ids for the subject
        db_content_ids = get_content_ids_by_ai_response_subject(subject, db)

        # Fetch content and associate it with the subject
        for content_id_tuple in db_content_ids:
            content_id = content_id_tuple[0]
            # Skip if content has already been processed
            if content_id in processed_content_ids:
                continue
            content = contents.get_content(content_id, db)
            subject_contents_map[subject].append(content)
            processed_content_ids.add(content_id)

    # Construct the result list
    result = [
        PromptSubjectAndContents(prompt=db_prompt, subject=subject, contents=contents)
        for subject, contents in subject_contents_map.items()
    ]

    return result
