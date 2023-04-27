from pydantic import BaseModel


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

json_format = "{basic_subjects:[{name,description},{name,description}], deeper_subjects:[{name,description},{name,description}]}"
