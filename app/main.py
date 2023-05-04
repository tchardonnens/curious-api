import logging
import os
import redis

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas.custom_response import CustomResponse
from app.schemas.youtube_response import YoutubeVideoSimple
from .routers import users
from .services.chatgpt import gpt_response
from .services.youtube import get_credentials, fetch_videos, search_videos
from .schemas.openai_response import Prompt


# Set the basic configuration for the logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%d-%m-%y %H:%M:%S",
)

app = FastAPI(
    title="Curious API",
    description="API for the Curious app",
    version="0.0.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    global cache
    pool = redis.ConnectionPool(
        host=os.getenv("REDIS_HOST"),
        port=os.getenv("REDIS_PORT"),
        db=os.getenv("REDIS_DB"),
        password=os.getenv("REDIS_PASSWORD"),
    )
    cache = redis.Redis(connection_pool=pool)


app.include_router(users.router)


@app.get("/", tags=["root"], response_description="Hello World")
async def root():
    return {"message": "Hello World"}


@app.post(
    "/chat",
    response_description="ChatGPT response",
    tags=["contents"],
)
async def chat(request: Prompt):
    if cache.get(request.prompt):
        logging.info("Cache hit")
        return {"message": cache.get(request.prompt)}
    else:
        logging.info("Cache miss")
        response = gpt_response(request.prompt)
        cache.set(request.prompt, response)
        return {"message": response}


@app.post(
    "/youtube",
    response_model=list[YoutubeVideoSimple],
    response_description="Youtube videos",
    tags=["contents"],
)
async def youtube_search(request: Prompt):
    videos = search_videos(request.prompt)
    return {"content": videos}


@app.post(
    "/curious",
    response_model=CustomResponse,
    response_description="ChatGPT response and Youtube videos",
    tags=["contents"],
)
async def curious(request: Prompt):
    if cache.get(request.prompt):
        response: str = cache.get(request.prompt)
    else:
        response: str = gpt_response(request.prompt)
        cache.set(request.prompt, response)

    credentials = await get_credentials()
    videos = fetch_videos(response, credentials)
    return {"chatgpt": response, "content": videos}


@app.on_event("shutdown")
async def shutdown_event():
    cache.close()
    logging.warning("Cache closed")
