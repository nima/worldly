#!/usr/bin/env python
import colored_traceback

# from dotenv import load_dotenv
# from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

import os
import sys
import json
from agents import quizzy
import ollama

colored_traceback.add_hook()


def recognize_state(text):
    messages = [
        {
            "role": "user",
            "content": f"""
                Given the string '{text}', which country, nation state, or city state is it in reference to?

                Your task is match the given text to the officially recognized name.  Three possibilities arise:
                1. It's clear what the country/state is, unambiguously, for example "China", or "Russia".
                2. It's ambiguous, for example "Congo"
                3. It's invalid, for example "Lilliput" or "Blefuscu"

                Don't return a sentence, such as "The country referred to is the People's Republic of China", but
                just the answe, i.e., "People's Republic of China".  Also use the official name, for example
                not "Russia", but "The Russian Federation".
                  
                In the second case, return a "?", and in the third case return a "!".
            """,
        }
    ]
    response = ollama.chat(model="mistral", messages=messages)
    return response["message"]["content"].strip()

    # messages.append({"role": "assistant", "content": response["message"]["content"]})
    # messages.append({"role": "user", "content": "And of Germany?"})

    # response = ollama.chat(model="mistral", messages=messages)
    # print(response["message"]["content"])


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
    # print(">>>%s<<<" % recognize_state("iran"))
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
