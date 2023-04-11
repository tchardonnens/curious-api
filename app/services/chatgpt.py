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
        template="ℹ️ More about {subject}. 📝 Paragraph please.",
    )
    chain = LLMChain(llm=llm, prompt=crafted_prompt)
    output = chain.run({"subject": prompt})
    return output

def gpt_list_response(prompt: str) -> list:
    crafted_prompt = PromptTemplate(
        input_variables=["subject"],
        template="List subjects to better understand {subject}.",
    )
    chain = LLMChain(llm=llm, prompt=crafted_prompt)
    output = chain.run({"subject": prompt})
    output_list = [item.split('. ')[1].strip() for item in output.split('\n') if item.strip() and '. ' in item]
    return output_list

def gpt_json_response(prompt: str) -> dict:
    crafted_prompt = PromptTemplate(
        input_variables=["json_format", "subject"],
        template="📚 JSON: {json_format} for {subject}.",
    )
    chain = LLMChain(llm=llm, prompt=crafted_prompt)
    response = chain.run({"json_format": json_format, "subject": prompt})
    print(response)
    data = json.loads(response)
    return data
