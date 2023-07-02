from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError

from app import models
from app.crud.response_prompt import (
    get_content_ids_by_ai_response_subject,
    get_response_prompts_by_id,
    get_three_response_prompts_by_id,
)
from app.schemas import prompts
from app.schemas.contents import SubjectResources, UserSubjectResources


def get_prompt_by_id(prompt_id: int, db: Session) -> models.Prompt:
    prompts = db.query(models.Prompt).filter(models.Prompt.id == prompt_id).first()
    if not prompts:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompts


def get_prompt_by_title(title: str, db: Session) -> models.Prompt:
    return db.query(models.Prompt).filter(models.Prompt.title == title).first()


def get_prompts_by_user_id(user_id: int, db: Session) -> list[models.Prompt]:
    prompts = db.query(models.Prompt).filter(models.Prompt.user_id == user_id).all()
    if not prompts:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompts


def get_last_three_public_prompts_by_user_id(
    user_id: int, db: Session
) -> list[models.Prompt]:
    prompts = (
        db.query(models.Prompt)
        .filter(models.Prompt.user_id == user_id)
        .filter(models.Prompt.is_private == False)
        .order_by(desc(models.Prompt.id))
        .limit(3)
        .all()
    )
    if not prompts:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompts


def get_last_three_prompts_by_user_id(user_id: int, db: Session) -> list[models.Prompt]:
    prompts = (
        db.query(models.Prompt)
        .filter(models.Prompt.user_id == user_id)
        .order_by(desc(models.Prompt.id))
        .limit(3)
        .all()
    )
    if not prompts:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompts


def get_prompts(db: Session, skip: int = 0, limit: int = 100) -> list[models.Prompt]:
    prompts = db.query(models.Prompt).offset(skip).limit(limit).all()
    if not prompts:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompts


def get_user_by_id(user_id: int, db: Session):
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail=f"User not found for id {user_id}")

    return user


def create_prompt(prompt: prompts.PromptCreate, db: Session) -> models.Prompt:
    db_prompt = get_prompt_by_title(title=prompt.title, db=db)
    if db_prompt:
        raise HTTPException(status_code=400, detail="Prompt already exists.")
    db_user = get_user_by_id(prompt.user_id, db)
    if db_user is None:
        raise HTTPException(status_code=400, detail="Invalid user ID.")
    try:
        db_prompt = models.Prompt(
            title=prompt.title,
            keywords=prompt.keywords,
            is_private=prompt.is_private,
            user_id=prompt.user_id,
        )
        db.add(db_prompt)
        db.commit()
        db.refresh(db_prompt)
        return db_prompt
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail="Failed to create prompt")


def switch_prompt_visibility(prompt_id: int, db: Session) -> models.Prompt:
    db_prompt = get_prompt_by_id(prompt_id, db)
    if db_prompt is None:
        raise HTTPException(status_code=400, detail="Prompt not found.")
    try:
        db_prompt.is_private = not db_prompt.is_private
        db.commit()
        db.refresh(db_prompt)
        return db_prompt
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def get_content_by_id(content_id: int, db: Session):
    return db.query(models.Content).filter(models.Content.id == content_id).first()


def get_prompt_contents(prompt_id: int, db: Session) -> UserSubjectResources:
    db_prompt = get_prompt_by_id(prompt_id, db)
    if db_prompt is None:
        raise HTTPException(status_code=400, detail="Prompt not found.")
    db_user = get_user_by_id(db_prompt.user_id, db)
    if db_user is None:
        raise HTTPException(status_code=400, detail="User not found.")
    db_response_prompts = get_three_response_prompts_by_id(prompt_id, db)
    if db_response_prompts is None:
        raise HTTPException(status_code=400, detail="No response prompts found.")
    db_contents = []
    for db_response_prompt in db_response_prompts:
        db_contents.append(get_content_by_id(db_response_prompt.content_id, db))

    return UserSubjectResources(
        user=db_user,
        prompt=db_prompt,
        subject=db_response_prompt.ai_response_subject,
        description=db_response_prompt.ai_response_description,
        contents=db_contents,
    )


def get_prompt_contents_history(prompt_id: int, db: Session) -> list[SubjectResources]:
    db_prompt = get_prompt_by_id(prompt_id, db)
    if db_prompt is None:
        raise HTTPException(status_code=400, detail="Prompt not found.")
    db_response_prompts = get_response_prompts_by_id(prompt_id, db)
    if db_response_prompts is None:
        raise HTTPException(status_code=400, detail="No response prompts found.")
    subject_contents_map = {}
    description_contents_map = {}

    processed_content_ids = set()

    for db_response_prompt in db_response_prompts:
        subject = db_response_prompt.ai_response_subject
        description = db_response_prompt.ai_response_description

        if subject not in subject_contents_map:
            subject_contents_map[subject] = []
            description_contents_map[subject] = description

        db_content_ids = get_content_ids_by_ai_response_subject(subject, db)

        for content_id_tuple in db_content_ids:
            content_id = content_id_tuple[0]
            if content_id in processed_content_ids:
                continue
            content = get_content_by_id(content_id, db)
            subject_contents_map[subject].append(content)
            processed_content_ids.add(content_id)

    result = [
        SubjectResources(
            prompt=db_prompt,
            subject=subject,
            description=description_contents_map[subject],
            contents=subject_contents_map[subject],
        )
        for subject in subject_contents_map.keys()
    ]

    return result
