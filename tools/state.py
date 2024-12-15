"""
This module provides all tools related to States; that is, political entities such Nation States,
City States, and Countries.
"""

from typing import Callable, Optional

# pylint: disable=unused-import
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.tools import Tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain import agents
from langchain import hub
from langchain.schema import AIMessage, ChatResult
import ollama
import openai


# Define the prompt template
TEMPLATE_BODY = """
You are a political scientist and geography expert. Your task is to match the given text 
to the officially recognized name of a country, nation-state, or city-state.

Rules:
- Always respond in strict JSON format.
- Do not include any explanatory text outside the JSON object.
- Valid values for the "type" key are:
    - "nation-state"
    - "city-state"
    - "capital-city"
    - "city"
    - "province", "state", "oblast", and so on, depending on the country
- Refer to the examples below for valid response structures.

Output:
- Always provide a valid JSON response based on the examples below.
- Respond only with the JSON block and nothing else.
- In the following json list, find sample objects that contain two keys, "intput", and
  "output".  Each time the LM is invoked, what it MUST return is an object with these
  two keys, where the input is the unaltered copy of the user input, and the output
  is the model's output.

Examples:
- Given "drc", return:
    {{
        "input": "drc",
        "output": {{
            "matches": [
                {{
                    "name": "Democratic Republic of the Congo",
                    "type": "nation-state"
                }}
            ]
        }}
    }}
- Given "usa", return:
    {{
        "input": "usa",
        "output": {{
            "matches": [
                {{
                    "name": "United States of America",
                    "type": "nation-state"
                }}
            ]
        }}
    }}
- Given "vatican", return:
    {{
        "input": "vatican",
        "output": {{
            "matches": [
                {{
                    "name": "Vatican City",
                    "type": "city-state"
                }}
            ]
        }}
    }}
- Given "congo", return:
    {{
        "input": "congo",
        "output": {{
            "matches": [
                {{
                    "name": "Democratic Republic of the Congo",
                    "type": "nation-state"
                }},
                {{
                    "name": "Republic of the Congo",
                    "type": "nation-state"
                }}
            ]
        }}
    }}
- Given "lilliput", return:
    {{
        "input": "lilliput",
        "output": {{
            "matches": []
        }}
    }}
- Given "damascus", return:
    {{
        "input": "damascus",
        "output": {{
            "matches": [
                {{
                    "name": "Damascus",
                    "type": "capital-city"
                }}
            ]
        }}
    }}
]
```

"""

TEMPLATE_QUESTION = """
# Question
Input: {payload}
"""

recognize_prompt_template = PromptTemplate(
    template=TEMPLATE_BODY + TEMPLATE_QUESTION, input_variables=["payload"]
)


# Create a helper to build a chain for any LLM
def _create_chain(llm: Callable) -> Callable:
    def _lm(payload: str) -> str:
        # Build the chain dynamically
        chain = recognize_prompt_template | llm | JsonOutputParser()
        return chain.invoke(input={"payload": payload})

    return _lm


# Functions for both OpenAI and Ollama LLMs
def _mklm_ollama(model="mistral") -> Callable:
    return ChatOllama(model=model, format="json")


def _mklm_openai(model="gpt-4o-mini") -> Callable:
    return ChatOpenAI(model=model, temperature=0)


# Define LLM-based functions
functions = {
    "OpenAI:gpt-4o-mini": _create_chain(_mklm_openai("gpt-4o-mini")),
    "Ollama:mistral": _create_chain(_mklm_ollama("mistral")),
}

# Define Tools
recognizers = [
    Tool(
        name=f"recognize_state_via_{lm}",
        func=func,
        description=(
            "Resolves user-provided text into the official name of a country, "
            "state, or region. Returns '?' for ambiguous inputs and '!' for invalid inputs."
        ),
    )
    for lm, func in functions.items()
]


# Note the wrapped function takes kwargs, and so when we wrap it in @tool, it will
# need that kwarg to be supplied via a dictionary.  That we we go
# - from: callable(a=1, b=2)
# - to:   tool.invoke({'a': 1, 'b': 2})
@agents.tool
def parse_lm_output(payload: dict) -> Optional[str]:
    """
    This function takes in a Python dictionary, and from that determins if the user's
    input is in fact a valid reference to a unique political State, either a nation state,
    or a city state.  It also requires that the said input be unambiguously tied to a
    single state.

    If there is no match, or if there are more than one matches, it will return None.

    If there is a single match, and that match is in fact a political state, then it
    will return the name of that state.

    Example payload = {{
        "input": "damascus",
        "output": {{
            "matches": [
                {{
                    "name": "Damascus",
                    "type": "capital-city"
                }}
            ]
        }}
    }}
    """
    output = payload["output"]
    if len(output["matches"]) != 1:
        return False

    matched = output["matches"][0]

    return matched["name"] if "state" in matched["type"] else None


def _recognize(engine, payload: str):
    """
    messages = []
    messages.append(
        {
            "role": "system",
            "format": "json",
            "content": TEMPLATE_BODY,
        }
    )
    messages.append({"role": "user", "format": "json", "content": payload})
    """
    try:
        messages = payload
        return engine(messages=messages)
    except Exception as e:
        raise RuntimeError("Error while communicating with the LLM") from e
