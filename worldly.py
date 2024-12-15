#!/usr/bin/env python
import json

import colored_traceback

# pylint: disable=unused-import
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.cache import InMemoryCache
from langchain import agents
from langchain import hub
import langchain

import tools.state

colored_traceback.add_hook()
langchain.cache = InMemoryCache()


def main():
    # print(quizzy.ask())

    # Executor
    llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
    toolbox = tools.state.recognizers
    prompts = {"react": hub.pull("hwchase17/react")}
    agent_react = agents.create_react_agent(
        llm=llm, tools=toolbox, prompt=prompts["react"]
    )
    _agent_json = agents.create_json_chat_agent(
        llm=llm, tools=toolbox, prompt=prompts["react"]
    )
    executor = agents.AgentExecutor(
        agent=agent_react, tools=toolbox, format="json", verbose=True
    )

    while True:
        user_input = input("What is the country you're thinking of? ")

        # Use the tool directly, without going via the Executor
        recognized = tools.state.functions["Ollama:mistral"](user_input)
        print(recognized)

        print(tools.state.parse_lm_output.invoke(input={"payload": recognized}))

        # Abstraction: Agent(Tools(Functions))
        # recognized = tools.state._recognize(user)
        # recognized = tools.state.recognize.run(user)
        recognized = executor.invoke(input={"input": user_input})
        print(recognized)


from langchain import hub

prompt = hub.pull("hwchase17/react")
prompt.template

if __name__ == "__main__":
    main()
