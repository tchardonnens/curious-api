from pydantic import BaseModel


class Prompt(BaseModel):
    prompt: str


class Subject(BaseModel):
    detailed_name: str


class AIResponse(BaseModel):
    basic_subjects: list[Subject]
    deeper_subjects: list[Subject]


json_template = """
Generate a realistic advice in the following JSON format:
---
    {
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

json_template_optimized = """
Generate a realistic advice in the following JSON format:
---
    {
        "basic_subjects": [
            {
                "detailed_name": ""
            },
            {
                "detailed_name": ""
            }
        ], 
        "deeper_subjects": [
            {
                "detailed_name": ""
            },
            {
                "detailed_name": ""
            }
        ]
    }
"""
