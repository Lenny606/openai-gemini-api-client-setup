from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# clientOA = OpenAI()
# clientGemini = OpenAI(
#     api_key="",
#     base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
# )
#
# responseOA = clientOA.chat.completions.create(
#     model="",
#     messages=[
#         {
#             "role": "user",
#             "content" : ""
#         }
#
#     ]
# )
#
# result = responseOA.choices[0].message.content

# OLLAMA
url = "http://localhost:11434/v1"
ollama = OpenAI(
    base_url=url,
    api_key="ollama" #its ignored, must be filled though
)
response = ollama.chat.completions.create(
    model="gemma3:270m",
    messages=[
        {
            "role": "user",
            "content" : "Hello"
        }

    ]
)
result = response.choices[0].message.content
print(result)