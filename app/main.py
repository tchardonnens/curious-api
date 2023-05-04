import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import contents, users

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

origins = [
    "https://verycurious.xyz",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(users.router)
app.include_router(contents.router)


@app.get("/", tags=["root"], response_description="Hello World")
async def root():
    return {"message": "Hello World"}
