#!/usr/bin/env python

"""This is Worldly's Quiz-Maker, a game to introduce basic LLM usage where the interaction with the
given model must be strictly controlled to the point that the conversation would be as constrained
as that with any non-generative API.

The idea for the quiz is simple:

Resources:
- A statically provided list of political State; The States list is just that, States; i.e., either
  City States, or Nation States, not provincess, not cities or capital cities, not towns, and so on.
- A set of dimensions, such as GDP, crime levels, top three exports or imports, and so on.  Note
  that some dimensionions will be numeric, while others are categoric.
- A set of LangChain tools, designed to interact with these dimensions.

The Game:
- The game engine begins by selecting one of the provided States by random.
- **LLM Step**: for the given selection, inspect all dimensions, and select a dimension based on:
  - **OpenAI Help**: This is where the LLM comes in, it should make decisions on dimension selection
    non-dry, and very interesting, sensible.  It should look at the user response, the country,
    the user's past guesses, and even past games, in order to do that.
- Once the dimension (or dimensions) have been selected, the question should be formed:
  - **OpenAI Help**: Again, here the LLM will use the dimensions selected, say for example land
    area, and also exports, to form a fun unique question that does not result in an answer that is
    extremely hard to guess (the question has very few answers), doesn't have too many answers (from
    all countries not guessed by the user so far, almost all will be correct).
- The user then writes what they think could be an answer.  The answer doesn't have to be the secret
  random pick, but if it meets the criteria posed by the game so far, that's still counted as a
  correct answer and gives points to the user.
- The user can also lose points if they provide a wrong answer that cannot be correct, such as the
  country is in the southern hemisphere, and the user selects USA.
- Once the model has selected their answer, the game assesses it, adds or deducts marks, and iterates
  to the next loop, until the user finds the right answer, or has wrongly ruled out the correct answer.
"""


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
    agent_react = agents.create_react_agent(llm=llm, tools=toolbox, prompt=prompts["react"])
    _agent_json = agents.create_json_chat_agent(llm=llm, tools=toolbox, prompt=prompts["react"])
    executor = agents.AgentExecutor(agent=agent_react, tools=toolbox, format="json", verbose=True)

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
