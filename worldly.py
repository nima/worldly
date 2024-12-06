#!/usr/bin/env python
# from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser

import os
import sys
import json
from agents import quizzy

evil = """
hitler
stalin
lenin
mao
khamenei
netanyahu
ben-gvir
hitler
"""


def sparse_dict(d):
    """
    Recursively remove keys with falsy values from a dictionary.
    """
    if isinstance(d, dict):
        return {
            key: sparse for key, value in d.items() if (sparse := sparse_dict(value))
        }

    if isinstance(d, list):
        return [sparse for item in d if (sparse := sparse_dict(item))]

    return d


def scrape_linkedin_profile():
    with open("mocked-linkedin-api-response.json", mode="r", encoding="utf-8") as file:
        return sparse_dict(json.load(file))


def main():
    # print(os.environ["OPENAI_API_KEY"])

    # prompt_template = PromptTemplate(
    #    input_variables=["dimensions"], template=prompt_template_fmt
    # )

    # llm = ChatOpenAI(temperature=0, model="gpt-4o")
    # llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
    # llm = ChatOllama(temperature=0, model="llama3")
    # llm = ChatOllama(temperature=0, model="mistral")

    # chain = prompt_template | llm | StrOutputParser()
    # res = chain.invoke(input={"dimensions": dimensions})
    # print(res)

    print(quizzy.ask())


if __name__ == "__main__":
    main()
