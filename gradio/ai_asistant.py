import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gradio as gr
from utils.prompts import system_prompt
from utils.tools import tool_structure
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

local_url = "http://localhost:11434/v1"
model = "llama3.2:1b"
dynamic = system_prompt
ollama = OpenAI(
    api_key="ollama",
    base_url=local_url
)

chat = OpenAI()

def get_ticket_prices(city):
    prices = {
        "prague": "52",
        "berlin": "55",
        "madrid": "99"
    }
    return prices[city.lower()] or "Unknown"


# define tools
price_function = tool_structure.copy()
price_function["name"] = "get_ticket_prices"
price_function["description"] = "Returns a ticket price for a given city"
price_function["description"] = "Returns a ticket price for a given city"
price_function["input_schema"]["type"] = "object"
price_function["input_schema"]["properties"] = {
    "city": {
        "type": "string",
        "description": "City name",
    }
}
price_function["input_schema"]["required"] = ["city"]

# Tools list
tools = [{"type": "function", "function": price_function}]


def chat(message, history):
    global dynamic
    dynamic += "You can use tools"
    messages = [{"role": "system", "content": dynamic}]
    messages = messages + history + [{"role": "user", "content": message}]
    res = ollama.chat.completions.create(model=model, messages=messages, tools=tools)
    print(res)
    if res.choices[0].finish_reason == "tool_calls":

        message = res.choices[0].message
        res = handle_tool_call(message)
        print(res)
        messages.append(res)  # reply from tool added to 2nd llm call
        res = ollama.chat.completions.create(model=model, messages=messages, tools=tools)

    return res.choices[0].message.content


def handle_tool_call(message):
    tool_call = message.tool_calls[0]
    if tool_call.function.name == "get_ticket_prices":
        args = json.loads(tool_call.function.arguments)
        city = args.get("city", None)
        print("Tool called: " + city or "Unknown")
        if city is not None:
            price = get_ticket_prices(city)
            response = {
                "role" : "tool",
                "content": price,
                "tool_call_id": tool_call.id,
            }
            return response

        return {
                "role" : "tool",
                "content": "No price found",
                "tool_call_id": tool_call.id,
            }



chat_ui = gr.ChatInterface(
    fn=chat, title="Plane Ticket Bot"
)
chat_ui.launch()
