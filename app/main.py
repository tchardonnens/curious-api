from fastapi import FastAPI
from services.chatgpt import chatgpt
from type.common import Prompt
import json

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "test"}

@app.post("/chat")
async def chat(request: Prompt):
    response = chatgpt(request.prompt)
    return {"message": response}
