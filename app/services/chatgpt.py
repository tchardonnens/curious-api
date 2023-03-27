import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def chatgpt(prompt: str) -> str:
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[
            {"role": "user", "content": "I want to know more about " + prompt + ". Give me ressoures to learn more about it and give me 2 subjects related with a depper complexity."}
        ]
    )
    return completion.choices[0].message.content
