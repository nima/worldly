from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import Tool
from langchain import agents
from langchain import hub

from worldly.play import dimensions


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

    # llm = ChatOllama(temperature=0, model="llama3")
    llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")

    prompt_template = PromptTemplate(
        input_variables=["dimensions"], template=prompt_template_fmt
    )

    tools = [
        Tool(
            name="dimension selector",
            func=dimensions,
            description="Used to select the next random dimension for the quiz",
        )
    ]

    prompts = {"react": hub.pull("hwchase17/react")}

    # dimensions = quiz_bank(None).dimensions
    # prompt = prompt_template.format_prompt(dimensions=dimensions)

    agent = agents.create_react_agent(
        llm=llm,
        tools=tools,
        prompt=prompts["react"],
    )

    serialized_objects = ", ".join(
        [f"dimension: {d.name}, effectiveness:{d.effectiveness}" for d in dimensions()]
    )
    executor = agents.AgentExecutor(agent=agent, tools=tools, verbose=True)
    input_data = {
        "input": f"""
            You are working with a list of Dimension objects. Each Dimension object has the following properties:

            - `name`: The name of the dimension (e.g., "landlocked", "gdp").
            - `effectiveness`: A numerical value between 0 and 1 representing how effective the
               dimension is at narrowing down possibilities.

            Your task is to:
            1. Analyze the list of Dimension objects provided.
            2. Select one dimension based on its `effectiveness` property, prioritizing dimensions with higher effectiveness scores.
            3. Create a quiz question based on the selected dimension.

            Here is how to interact with the Dimension objects:
            - Access the name with `.name`.
            - Access the effectiveness score with `.effectiveness`.

            Proceed with the list of Dimension objects and provide:
            - The name of the selected dimension.
            - Your reasoning for the selection.
            - The quiz question.

            The answer to your question must always be a country, nation state, or city state.

            You are working with the following Dimensions (serialized):
            {serialized_objects}
        """
    }
    result = executor.invoke(input=input_data)
    print("Agent Result:", result)

    # Providing a placeholder input to invoke

    # chain = prompt_template | llm | StrOutputParser()
    # dimensions = quiz_bank().dimensions
    # question = chain.invoke(input={"dimensions": dimensions})
    # return question

    return result["output"]
