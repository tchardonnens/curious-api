import os
import asyncio
import httpx
import logging
from app.crud import contents, response_prompt
from app import models
from app.schemas.response_prompt import ResponsePromptCreate
from app.schemas.contents import ContentBase, SubjectResources

# Configuration
SEARCH_API_KEY = os.environ["SEARCH_API_KEY"]
SEARCH_ENGINE_IDS = {
    "youtube": os.environ["YOUTUBE_SEARCH_ENGINE_ID"],
    "reddit": os.environ["REDDIT_SEARCH_ENGINE_ID"],
    "twitter": os.environ["TWITTER_SEARCH_ENGINE_ID"],
}
BASE_URL = "https://www.googleapis.com/customsearch/v1"

# Logger configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def parse_search_results(search_items, source):
    """
    Cleans up search results received from Google Custom Search.
    """
    cleaned_results = []
    for search_item in search_items:
        try:
            metatags = search_item["pagemap"]["metatags"][0]
            cleaned_results.append(
                ContentBase(
                    title=search_item.get("title", "N/A"),
                    snippet=search_item.get("snippet", "N/A"),
                    link=search_item.get("link", "N/A"),
                    long_description=metatags.get("og:description", "N/A"),
                    image=metatags.get("og:image", "N/A"),
                    source=source,
                )
            )
        except KeyError:
            continue
    return cleaned_results


async def search(query, search_engine_id):
    """
    Performs a search using Google Custom Search Engine.
    """
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
            logger.error(f"An HTTP error occurred: {exc}")
            return []
        except Exception as exc:
            logger.error(f"An error occurred: {exc}")
            return []


async def store_results(
    prompt: models.Prompt,
    ai_response_subject: str,
    ai_response_description: str,
    search_results,
    db,
):
    """
    Stores the search results in the database.
    """

    async def save_results_to_db(results, source, prompt_id, db):
        contents_list = []
        for result in results:
            content = contents.create_content(result, source, db)
            contents_list.append(content)
            response_prompt.create_response_prompt(
                ResponsePromptCreate(
                    prompt_id=prompt_id,
                    content_id=content.id,
                    ai_response_subject=ai_response_subject,
                    ai_response_description=ai_response_description,
                ),
                db,
            )
        return contents_list

    aggregated_results = []
    for source, results in search_results.items():
        aggregated_results.extend(
            await save_results_to_db(results, source, prompt.id, db)
        )

    return SubjectResources(
        prompt=prompt,
        subject=ai_response_subject,
        description=ai_response_description,
        contents=aggregated_results,
    )


async def search_resources(
    prompt_in_db: models.Prompt,
    ai_response_subject: str,
    ai_response_description: str,
    db,
):
    """
    Searches and processes the subject using various search engines.
    """
    query = f"{prompt_in_db.keywords} {ai_response_subject}"

    # Perform searches in parallel
    search_tasks = {
        source: parse_search_results(await search(query, search_engine_id), source)
        for source, search_engine_id in SEARCH_ENGINE_IDS.items()
    }

    # Wait for all searches to complete
    search_results_raw = await asyncio.gather(*search_tasks.values())

    # Rebuilding dictionary with sources and results
    search_results = dict(zip(search_tasks.keys(), search_results_raw))

    # Store results and return
    return await store_results(
        prompt_in_db, ai_response_subject, ai_response_description, search_results, db
    )
