import os
import openai
import json
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from type.openai_response import json_format

openai.api_key = os.getenv("OPENAI_API_KEY")

llm = OpenAI(temperature=0.9)

def gpt_response(prompt: str) -> str:
    crafted_prompt = PromptTemplate(
        input_variables=["subject"],
        template="I want to know more about {subject}. Give me a paragraph to understand it better.",
    )
    chain = LLMChain(llm=llm, prompt=crafted_prompt)
    output = chain.run({"subject": prompt})
    return output

def gpt_list_response(prompt: str) -> list:
    crafted_prompt = PromptTemplate(
        input_variables=["subject"],
        template="I want to know more about {subject}. Give a list of subjects to study to understand it better.",
    )
    chain = LLMChain(llm=llm, prompt=crafted_prompt)
    output = chain.run({"subject": prompt})
    output_list = [item.split('. ')[1].strip() for item in output.split('\n') if item.strip() and '. ' in item]
    return output_list

def gpt_json_response(prompt: str) -> dict:
    crafted_prompt = PromptTemplate(
        input_variables=["subject", "json_format"],
        template="I want to know more about {subject}. Format it in the following JSON: {json_format}",
    )
    chain = LLMChain(llm=llm, prompt=crafted_prompt)
    response = chain.run({"subject": prompt, "json_format": json_format})
    print(response)
    data = json.loads(response)
    return data
