import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gradio as gr
from utils.prompts import system_prompt
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

local_url = "http://localhost:11434/v1"
model = "llama3.2:1b"

ollama = OpenAI(
    api_key="ollama",
    base_url=local_url
)


def chat(message, history):
    # format history metadata if needed

    # dynamic system prompt to use clever input context
    dynamic_system_prompt = system_prompt
    if "belt" in message.lower():
        dynamic_system_prompt = "Your are belt specialist, try to sell belts"

    messages = [
        {
            "role": "system",
            "content": dynamic_system_prompt
        }
    ]

    messages = messages + history + [{"role": "user", "content": message}]
    res = ollama.chat.completions.create(model=model, messages=messages, stream=True)
    result = ""

    for chunk in res:
        result += chunk.choices[0].delta.content or ""
        yield result


chat_ui = gr.ChatInterface(
    fn=chat, title="Chat Bot"
)
chat_ui.launch()
