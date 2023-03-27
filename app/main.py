from fastapi import FastAPI
from services.chatgpt import chatgpt
from services.youtube import get_credentials, search_videos
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
    videos = []
    # Initialize youtube service
    credentials = await get_credentials()
    for subject in basic_subjects:
        videos.append(search_videos(subject["name"], credentials))
    for subject in deeper_subjects:
        videos.append(search_videos(subject["name"], credentials))
    return {"message": response, "content": videos}
