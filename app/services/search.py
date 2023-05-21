import os
import asyncio
import httpx

from app.schemas.custom_response import CleanGoogleResult, AllSourcesCleanGoogleResult

SEARCH_API_KEY = os.getenv("SEARCH_API_KEY")
YOUTUBE_SEARCH_ENGINE_ID = os.getenv("YOUTUBE_SEARCH_ENGINE_ID")
REDDIT_SEARCH_ENGINE_ID = os.getenv("REDDIT_SEARCH_ENGINE_ID")
TWITTER_SEARCH_ENGINE_ID = os.getenv("TWITTER_SEARCH_ENGINE_ID")

BASE_URL = "https://www.googleapis.com/customsearch/v1"


async def __parseResults__(search_items) -> list[CleanGoogleResult]:
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
                CleanGoogleResult(
                    title=title,
                    snippet=snippet,
                    link=link,
                    long_description=long_description,
                    image=image,
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
        except httpx.HTTPStatusError as exc:
            print(f"An HTTP error occurred: {exc}")
        except Exception as exc:
            print(f"An error occurred: {exc}")
        return resp.json().get("items", [])


async def querySearchEngines(query: str) -> AllSourcesCleanGoogleResult:
    youtube_results, reddit_results, twitter_results = await asyncio.gather(
        __parseResults__(await __search__(query, YOUTUBE_SEARCH_ENGINE_ID)),
        __parseResults__(await __search__(query, REDDIT_SEARCH_ENGINE_ID)),
        __parseResults__(await __search__(query, TWITTER_SEARCH_ENGINE_ID)),
    )
    return AllSourcesCleanGoogleResult(
        youtube=youtube_results, reddit=reddit_results, twitter=twitter_results
    )
