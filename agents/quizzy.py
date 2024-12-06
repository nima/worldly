from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import Tool
from langchain import agents
from langchain import hub

from worldly.dimensions import Dimension, DataDotWorld
from worldly.play import quiz_bank


def ask() -> str:
    prompt_template_fmt = """I want to construct a quiz loop, where we ask the user 
    successive questions, and lead the user to guess what country we're thinking of.

    To do that, I have constructed a set of dimensions, each focused on only one
    dimension, such as GDP, or if the country is land-locked or not.

    Here's how it works:
    1. You select a country that you keep secret
    2. You then select a random dimension, from the dimensions list that I will be
    providing to you.
    3. You use the given dimension to construct a statement which is true for at
    least the secret country you've thought of.

    Here are the relevant metadata heuristics for question composition:
        dimensions: {dimensions}
        output_indicator: the question alone
    """

    llm = ChatOllama(temperature=0, model="llama3")

    prompt_template = PromptTemplate(
        input_variables=["dimensions"], template=prompt_template_fmt
    )

    tools = [
        Tool(
            name="dimension selector",
            func=quiz_bank,
            description="Used to select the next random dimension for the quiz",
        )
    ]

    prompts = {"react": hub.pull("hwchase17/react")}
    agent = agents.create_react_agent(
        llm=llm,
        tools=tools,
        prompt=prompts["react"],
    )
    executor = agents.AgentExecutor(agent=agent, tools=tools, verbose=True)

    dimensions = quiz_bank(None).dimensions
    prompt = prompt_template.format_prompt(dimensions=dimensions)
    result = executor.invoke(input={"input": prompt})

    # chain = prompt_template | llm | StrOutputParser()
    # dimensions = quiz_bank().dimensions
    # question = chain.invoke(input={"dimensions": dimensions})
    # return question

    print(result)

    return result["output"]
