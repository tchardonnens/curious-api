import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api_analytics.fastapi import Analytics

from .routers import contents, users, prompts

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%d-%m-%y %H:%M:%S",
)

app = FastAPI(
    title="Curious API",
    description="API for the Curious app",
    version="0.6.0",
)

origins = [
    "http://localhost:3000",
    "https://verycurious.xyz",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    Analytics,
    api_key=os.getenv("ANALYTICS_API_KEY"),
)


app.include_router(users.router)
app.include_router(contents.router)
app.include_router(prompts.router)


@app.get("/", tags=["root"], response_description="Hello World")
async def root():
    return {"message": "Hello World"}
