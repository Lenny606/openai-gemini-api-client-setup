import json
import requests
from typing import Literal, Optional
from openai import OpenAI
from dotenv import load_dotenv
import os
from pydantic import BaseModel, Field

load_dotenv()
gemini_key = os.getenv("GEMINI_API_KEY")

# gemini compatible
geminiClient = OpenAI(
    api_key=gemini_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)


def get_weather(city: str) -> str:
    """
    Fetches the current weather for a specified city. The weather information includes 
    the condition and temperature. The function sends an HTTP request to a weather 
    API to retrieve the data.

    :param city: Name of the city to fetch the weather for.
    :type city: str
    :return: Weather condition and temperature in the specified city.
    :rtype: str
    """
    response = requests.get(f"https://wttr.in/{city.lower()}?format=%C+%t")
    if response.status_code != 200:
        return {"error": f"Failed to fetch weather for {city}"}
    return f"Weather in {city}: {response.text}"


CHAIN_OF_THOUGHT_PROMPT = """
System prompt (Chain-of-Thought safe template):
You are an expert agentic AI assistant with access to various tools. Solve tasks by using your tools and deep internal reasoning, but do not reveal your chain-of-thought.

Policy:
- Perform step-by-step reasoning privately (do not output it).
- Output only: the final answer, a very brief justification (1–3 sentences), and the code/results required.
- If asked for your reasoning or to show steps, politely decline and provide a concise answer instead.
- Prefer correctness, determinism, and security. Handle edge cases. Follow the requested format strictly.
- Use tools when needed to get additional data by calling tool functions, for example:
  To get weather: Use get_weather("London") to fetch current weather in London
  
Available tools:
- get_weather(city: str) -> str: Get current weather conditions for a city

Output format for different tasks:

For coding tasks:
- Summary: one-sentence description of what the code does.
- Code: a single, self-contained snippet.
- Notes: up to 3 bullet points with key caveats or next steps (optional).

For tool usage tasks:
- Summary: one-sentence description of what you'll do.
- Tool call: tool_name(parameters)
- Result: <tool output>
- Notes: up to 3 bullet points with key findings (optional).

Example coding task:
User: Write a Python function `is_palindrome(s: str) -> bool` that returns True if string is palindrome
Assistant:
Summary: Checks whether a string is a palindrome ignoring case and non-alphanumerics.
Code:"""

PromptMode = Literal["zero", "few", "cot"]

system_prompt = CHAIN_OF_THOUGHT_PROMPT

message_history = [
    {"role": "system", "content": system_prompt}
]

# add history
user_query = input("Enter: ")
message_history.append({"role": "user", "content": user_query})


# Schema
class OutputFormat(BaseModel):
    step: str = Field(..., description="ID of step in chain of though")
    content: Optional[str] = Field(None, description="Optional content of step")
    tool: Optional[str] = Field(None, description="Optional tool used in step")
    input: Optional[str] = Field(None, description="Optional input to tool")


while True:
    responseGemini = geminiClient.chat.completions.parse(
        model="gemini-2.5-flash",
        messages=message_history,
        response_format=OutputFormat
    )

    raw_output = responseGemini.choices[0].message.content

    # Check if content exists
    if raw_output is None:
        print("Chyba: Model nevrátil žádný obsah. Zkuste jiný dotaz.")
        user_query = input("Enter: ")
        message_history.append({"role": "user", "content": user_query})
        continue

    # Check for tool usage pattern
    if "Tool call:" in raw_output:
        tool_lines = [line.strip() for line in raw_output.split('\n') if line.strip()]
        for line in tool_lines:
            if line.startswith("Tool call: get_weather"):
                # Extract city parameter
                city = line.split('get_weather("')[1].split('")')[0]
                weather_result = get_weather(city)
                # Add tool result to conversation
                message_history.append({"role": "assistant", "content": raw_output})
                message_history.append({"role": "system", "content": f"Tool result: {weather_result}"})
                raw_output += f"\nResult: {weather_result}"

    message_history.append({"role": "assistant", "content": raw_output})
    print(raw_output)
