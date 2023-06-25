from pydantic import BaseModel


class AIPrompt(BaseModel):
    prompt: str


class Subject(BaseModel):
    detailed_name: str
    description: str


class AIResponse(BaseModel):
    main_subject_of_the_prompt: str
    basic_subjects: list[Subject]
    deeper_subjects: list[Subject]


json_template = """
Generate a realistic advice in the following JSON format:
---
    {
        "main_suject_of_the_prompt": "",
        "basic_subjects": [
            {
                "detailed_name": "",
                "description": ""
            },
            {
                "detailed_name": "",
                "description": ""
            }
        ],
        "deeper_subjects": [
            {
                "detailed_name": "",
                "description": ""
            },
            {
                "detailed_name": "",
                "description": ""
            }
        ]
    }
"""
