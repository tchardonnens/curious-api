from fastapi import FastAPI
from services.chatgpt import chatgpt
from services.youtube import get_credentials, fetch_videos, search_videos
from type.common import Prompt

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "test"}

@app.post("/chat")
async def chat(request: Prompt):
    response = chatgpt(request.prompt)
    return {"message": response}

@app.post("/youtube")
async def youtube_search(request: Prompt):
    videos = search_videos(request.prompt)
    return {"content": videos}

@app.post("/curious")
async def curious(request: Prompt):
    response = chatgpt(request.prompt)
    basic_subjects = response["resources"][0]["basic_subjects"]
    deeper_subjects = response["resources"][1]["deeper_subjects"]
    credentials = await get_credentials()
    videos = fetch_videos(basic_subjects, deeper_subjects, credentials)
    return {"chatgpt": response, "content": videos}
