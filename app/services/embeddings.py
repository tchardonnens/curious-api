from langchain.embeddings import OpenAIEmbeddings
from requests import Session

from app import models


def create_embeddings(text: str) -> list:
    embeddings = OpenAIEmbeddings()
    return embeddings.embed_query(text)
