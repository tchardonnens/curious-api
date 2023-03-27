import os
import openai
import json
from type.openai_response import json_format

openai.api_key = os.getenv("OPENAI_API_KEY")

def chatgpt(prompt: str) -> dict:
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[
            {
                "role": "user", 
                "content": "I want to know more about " + prompt + ". Format it in the following JSON: " + json_format
            }
        ]
    )
    message = completion.choices[0].message.content
    data = json.loads(message)
    return data
