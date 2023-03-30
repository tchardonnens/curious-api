from pydantic import BaseModel

# https://developers.google.com/youtube/v3/docs/search/list
# https://developers.google.com/youtube/v3/docs/search#resource

class YoutubeVideoId(BaseModel):
    kind: str
    videoId: str
    channelId: str
    playlistId: str

class YoutubeVideoSnippet(BaseModel):
    publishedAt: str
    channelId: str
    title: str
    description: str
    thumbnails: dict
    channelTitle: str
    liveBroadcastContent: str

class YoutubeVideoSnippetThumbnails(BaseModel):
    url: str
    width: int
    height: int

class YoutubeVideo(BaseModel):
    kind: str
    etag: str
    id: str
    snippet: dict

class PageInfo(BaseModel):
    totalResults: int
    resultsPerPage: int

class YoutubeSearchList(BaseModel):
    kind: str
    etag: str
    nextPageToken: str
    prevPageToken: str
    regionCode: str
    pageInfo: dict
    items: list[YoutubeVideo]

## Simplified custom response

class YoutubeVideoSimple(BaseModel):
    title: str
    description: str
    url: str
    thumbnail: str
