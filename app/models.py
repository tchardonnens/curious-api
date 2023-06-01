from sqlalchemy import Boolean, Column, Integer, String

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    username = Column(String, unique=True, index=True)
    full_name = Column(String, index=True)
    is_active = Column(Boolean, default=True)


class Content(Base):
    __tablename__ = "contents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True)
    description = Column(String, unique=True, index=True)
    url = Column(String, index=True)
    is_active = Column(Boolean, default=True)


class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True)
    user_id = Column(Integer, index=True)
    created_at = Column(String, index=True)


class ResponsePrompt(Base):
    __tablename__ = "response_prompts"

    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(Integer, index=True)
    content_id = Column(Integer, index=True)
    created_at = Column(String, index=True)
