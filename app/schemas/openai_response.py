from pydantic import BaseModel


class Prompt(BaseModel):
    prompt: str


class ChatGPTUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatGPTMessage(BaseModel):
    role: str
    content: str


class ChatGPTChoice(BaseModel):
    message: ChatGPTMessage
    finish_reason: str
    index: int


class ChatGPTResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    usage: ChatGPTUsage
    choices: ChatGPTChoice


class Subject(BaseModel):
    name: str
    description: str


class AIResponse(BaseModel):
    basic_subjects: list[Subject]
    deeper_subjects: list[Subject]


json_template = """
Generate a realistic advice in the following JSON format:
---
    {
        "basic_subjects": [
            {
                "name": "",
                "description": ""
            },
            {
                "name": "",
                "description": ""
            }
        ], 
        "deeper_subjects": [
            {
                "name": "",
                "description": ""
            },
            {
                "name": "",
                "description": ""
            }
        ]
    }
"""
