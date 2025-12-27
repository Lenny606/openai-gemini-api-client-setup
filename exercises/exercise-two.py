import requests
from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

claude_api_key = os.getenv("ANTHROPIC_API_KEY")
oa_api_key = os.getenv("OPENAI_API_KEY")
claude_url = "https://api.anthropic.com/v1/"
# print(claude_api_key[:15])

groq_api_key = os.getenv("GROQ_API_KEY")
groq_url = "https://api.groq.com/openai/v1/"
groq_model = "openai/gpt-oss-120b"

local_url = "http://localhost:11434/v1"
# send localu
# requests.get(local_url).content

llm = OpenAI(
    api_key=groq_api_key,
    base_url=groq_url
)

ollama = OpenAI(
    api_key="ollama",
    base_url=local_url
)

message = [
    {
        "role": "user",
        "content": "tell a joke"
    }
]

# r = llm.chat.completions.create(
#     model=groq_model,
#     messages=message,
#     ) #reasoning_effort="minimal"

r = ollama.chat.completions.create(
    model="llama3.2:1b",
    messages=message,
)
print(r.choices[0].message.content)
