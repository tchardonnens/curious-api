from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    username = Column(String, unique=True, index=True)
    full_name = Column(String, index=True)
    bio = Column(String, index=True, default="Lorem ipsum")
    profile_picture = Column(
        String,
        index=True,
        default="https://media.licdn.com/dms/image/D4E03AQFuIj2EaSDYbg/profile-displayphoto-shrink_400_400/0/1685128811345?e=1692230400&v=beta&t=KeMgavxd3GBhIJLcYvQZtsv4yeNg3LdPsYzHQZ41MQw",
    )
    profile_banner = Column(
        String,
        index=True,
        default="https://pbs.twimg.com/profile_banners/1500074670917312513/1646482168/1500x500",
    )
    is_active = Column(Boolean, default=True)
    prompts = relationship("Prompt", backref="user")


class Content(Base):
    __tablename__ = "contents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    snippet = Column(String, index=True)
    link = Column(String, index=True)
    source = Column(String, index=True)
    long_description = Column(String, index=True)
    image = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    responses = relationship("ResponsePrompt", backref="content")


class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    keywords = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    responses = relationship("ResponsePrompt", backref="prompt")


class ResponsePrompt(Base):
    __tablename__ = "response_prompts"

    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id"), index=True)
    content_id = Column(Integer, ForeignKey("contents.id"), index=True)
    ai_response_subject = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class follows(Base):
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    follow_id = Column(Integer, ForeignKey("users.id"), index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
