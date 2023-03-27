from fastapi import FastAPI
from services.chatgpt import chatgpt
from services.youtube import search
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
    videos = search(request.prompt)
    return {"content": videos}
