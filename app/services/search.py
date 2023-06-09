import os
import asyncio
import httpx
from app.crud import contents, response_prompt
from app.schemas.prompts import Prompt
from app.schemas.response_prompt import ResponsePromptCreate
from sqlalchemy.orm import Session

from app.schemas.contents import (
    Content,
    ContentBase,
    PromptSubjectAndContents,
)

SEARCH_API_KEY = os.getenv("SEARCH_API_KEY")
YOUTUBE_SEARCH_ENGINE_ID = os.getenv("YOUTUBE_SEARCH_ENGINE_ID")
REDDIT_SEARCH_ENGINE_ID = os.getenv("REDDIT_SEARCH_ENGINE_ID")
TWITTER_SEARCH_ENGINE_ID = os.getenv("TWITTER_SEARCH_ENGINE_ID")

BASE_URL = "https://www.googleapis.com/customsearch/v1"


async def __parse_results__(search_items, source) -> list[ContentBase]:
    cleaned_results = []
    for search_item in search_items:
        try:
            long_description = search_item["pagemap"]["metatags"][0].get(
                "og:description", "N/A"
            )
            image = search_item["pagemap"]["metatags"][0].get("og:image", "N/A")
            title = search_item.get("title", "N/A")
            snippet = search_item.get("snippet", "N/A")
            link = search_item.get("link", "N/A")
            cleaned_results.append(
                ContentBase(
                    title=title,
                    snippet=snippet,
                    link=link,
                    long_description=long_description,
                    image=image,
                    source=source,
                )
            )
        except KeyError:
            continue
    return cleaned_results


async def __search__(query: str, search_engine_id: str):
    async with httpx.AsyncClient() as client:
        params = {
            "key": SEARCH_API_KEY,
            "cx": search_engine_id,
            "q": query,
            "start": 1,
            "num": 2,
        }
        try:
            resp = await client.get(BASE_URL, params=params)
            resp.raise_for_status()
            return resp.json().get("items", [])
        except httpx.HTTPStatusError as exc:
            print(f"An HTTP error occurred: {exc}")
            return []
        except Exception as exc:
            print(f"An error occurred: {exc}")
            return []


async def save_search_and_results(
    created_prompt: Prompt,
    ai_response_subject: str,
    ai_response_description: str,
    youtube_results: list[Content],
    reddit_results: list[Content],
    twitter_results: list[Content],
    db: Session,
) -> PromptSubjectAndContents:
    async def save_results(
        results: list[ContentBase], source: str, created_prompt_id: int, db: Session
    ):
        list_of_contents: list[Content] = []
        for result in results:
            created_content: Content = contents.create_content(result, source, db)
            list_of_contents.append(created_content)
            response_prompt.create_response_prompt(
                ResponsePromptCreate(
                    prompt_id=created_prompt_id,
                    content_id=created_content.id,
                    ai_response_subject=ai_response_subject,
                    ai_response_description=ai_response_description,
                ),
                db,
            )
        return list_of_contents

    youtube_results = await save_results(
        youtube_results, "youtube", created_prompt.id, db
    )
    reddit_results = await save_results(reddit_results, "reddit", created_prompt.id, db)
    twitter_results = await save_results(
        twitter_results, "twitter", created_prompt.id, db
    )

    all_sources_content = youtube_results + reddit_results + twitter_results

    return PromptSubjectAndContents(
        prompt=created_prompt,
        subject=ai_response_subject,
        description=ai_response_description,
        contents=all_sources_content,
    )


async def LLMResponseSubjectSearchEngines(
    prompt: Prompt, ai_response_subject: str, ai_response_description: str, db: Session
) -> PromptSubjectAndContents:
    query = f"{prompt.keywords} {ai_response_subject}"
    youtube_results, reddit_results, twitter_results = await asyncio.gather(
        __parse_results__(await __search__(query, YOUTUBE_SEARCH_ENGINE_ID), "youtube"),
        __parse_results__(await __search__(query, REDDIT_SEARCH_ENGINE_ID), "reddit"),
        __parse_results__(await __search__(query, TWITTER_SEARCH_ENGINE_ID), "twitter"),
    )
    stored_data = await save_search_and_results(
        prompt,
        ai_response_subject,
        ai_response_description,
        youtube_results,
        reddit_results,
        twitter_results,
        db,
    )
    return stored_data
