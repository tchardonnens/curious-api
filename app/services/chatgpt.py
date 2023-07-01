from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.output_parsers import OutputFixingParser
from langchain.output_parsers import PydanticOutputParser

from app.schemas.openai_response import (
    json_template,
    LLMResponse,
)

llm = OpenAI(temperature=0.4)


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
    output_list = [
        item.split(". ")[1].strip()
        for item in output.split("\n")
        if item.strip() and ". " in item
    ]
    return output_list


def gpt_json_response(prompt: str) -> dict:
    crafted_prompt = PromptTemplate(
        input_variables=["json_format", "subject"],
        template="{json_format} \n The advice is about {subject}.",
    )
    chain = LLMChain(llm=llm, prompt=crafted_prompt)
    ai_response = chain.run({"json_format": json_template, "subject": prompt})
    parser = PydanticOutputParser(pydantic_object=LLMResponse)

    try:
        print("Trying to parse...")
        res: LLMResponse = parser.parse(ai_response)
    except Exception as e:
        print("Error in JSON... Fixing...")
        new_parser = OutputFixingParser.from_llm(parser=parser, llm=ChatOpenAI())
        res = new_parser.parse(ai_response)

    return res
