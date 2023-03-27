# -*- coding: utf-8 -*-

# Sample Python code for youtube.search.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python

import os
import json

from google_auth_oauthlib.flow import InstalledAppFlow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def search(query: str) -> dict:
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "../code_secret_client_69757901097-d2obr9058sh75jittfvnd8uf6mffhlt4.apps.googleusercontent.com.json"

    # Get credentials and create an API client
    flow = InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_local_server(port=8080)
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    request = youtube.search().list(
        part="snippet",
        # order="rating",
        q=query,
        # safeSearch="strict",
        # videoDimension="any",
        # videoDuration="medium"
    )
    response = request.execute()
    return response