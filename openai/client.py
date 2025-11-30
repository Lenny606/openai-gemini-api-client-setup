from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
gemini_key = os.getenv("GEMINI_API_KEY")

client = OpenAI()
response = client.responses.create(
    model="gpt-4o-mini",
    input="What day is today?"
)

#gemini compatible
geminiClient = OpenAI(
    api_key=gemini_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

responseGemini = geminiClient.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Explain to me how AI works"
        }
    ]
)

print(response.output_text)
print(responseGemini.choices[0].message.content)
