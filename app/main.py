from fastapi import FastAPI
from services.chatgpt import gpt_response
from services.youtube import get_credentials, fetch_videos, search_videos
from type.common import Prompt
from fastapi.middleware.cors import CORSMiddleware
import redis

app = FastAPI()

# allow CORS for localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event('startup')
async def startup_event():
    global cache
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    cache = redis.Redis(connection_pool=pool)

@app.get("/")
async def root():
    return {"message": "test"}

@app.post("/chat")
async def chat(request: Prompt):
    if cache.get(request.prompt):
        print("Cache hit")
        return {"message": cache.get(request.prompt)}
    else:
        print("Cache miss")
        response = gpt_response(request.prompt)
        cache.set(request.prompt, response)
        return {"message": response}

@app.post("/youtube")
async def youtube_search(request: Prompt):
    videos = search_videos(request.prompt)
    return {"content": videos}

@app.post("/curious")
async def curious(request: Prompt):
    if cache.get(request.prompt):
        response = cache.get(request.prompt)
    else:
        response = gpt_response(request.prompt)
        cache.set(request.prompt, response)

    credentials = await get_credentials()
    videos = fetch_videos(response, credentials)
    return {"chatgpt": response, "content": videos}

@app.on_event("shutdown")
async def shutdown_event():
    cache.close()
    print("Cache closed")
