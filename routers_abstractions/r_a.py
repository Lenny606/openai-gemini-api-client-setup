#router = directs to diff providers (OpenRouter ai)
#abstraction => frameworks
import os
from dotenv import load_dotenv

load_dotenv()

#same config using OA client a OR key

from openai import OpenAI
from langchain_openai import ChatOpenAI
# LITE LLM
from litellm import completion

# llm = OpenAI(
#     api_key=os.getenv("OPEN_ROUTER_API_KEY"),
#     base_url=os.getenv("OPEN_ROUTER_API_URL")
# )
# r = llm.chat.completions.create(
#     model="z-ai/glm-4.5",
#     messages= ""
# )

chat = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o-mini"
)
message = [
    {
        "role": "user",
        "content": "tell a joke"
    }
]

response = completion(model="gpt-4o-mini", messages=message)

# res = chat.invoke(message)

print(response.choices[0].message.content)

# CACHING PROMPT !!!!!!! (implicit / explicit)