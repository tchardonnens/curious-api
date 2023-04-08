# -*- coding: utf-8 -*-

# Sample Python code for youtube.search.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python

import os

from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
import googleapiclient.discovery
import googleapiclient.errors

from type.youtube_response import YoutubeSearchList, YoutubeVideoSimple

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
api_service_name = "youtube"
api_version = "v3"

async def get_credentials() -> Credentials:
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    client_secrets_file = "../code_secret_client_69757901097-d2obr9058sh75jittfvnd8uf6mffhlt4.apps.googleusercontent.com.json"

    # Get credentials and create an API client
    flow = InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_local_server(port=8080)
    return credentials

def search_videos(query: str, credentials) -> YoutubeSearchList:
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)
    request = youtube.search().list(
        part="snippet",
        # order="rating",
        q=query,
        safeSearch="strict",
        # videoDimension="any",
        # videoDuration="medium"
    )
    response = request.execute()
    return response

def __scroll_videos__(subject, credentials: Credentials) -> list[YoutubeVideoSimple]:
    yt_videos_list = search_videos(subject, credentials)
    videos = []
    # check if there are videos
    if yt_videos_list["items"]:
        for video in yt_videos_list["items"]:
            # check if the video has an id
            if "videoId" in video["id"]:
                video_info = YoutubeVideoSimple(
                    title=video["snippet"]["title"],
                    description=video["snippet"]["description"],
                    url=f"https://www.youtube.com/watch?v={video['id']['videoId']}",
                    thumbnail=video["snippet"]["thumbnails"]["default"]["url"]
                )
                videos.append(video_info)
    return videos

def fetch_videos(subjects: list, credentials: Credentials) -> list[YoutubeVideoSimple]:
    videos = []
    for subject in subjects:
        videos.append(__scroll_videos__(subject, credentials))
    return videos
