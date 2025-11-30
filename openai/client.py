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

# gemini compatible
geminiClient = OpenAI(
    api_key=gemini_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

ZERO_SHOT = "Give only coding answers to question, if not possible , say sorry."
FEW_SHOT_PROMPT = """Give only coding answers to question, if not possible , say sorry. 
                Rule: follow JSON output format in answers
                
                Output Format:
                {{
                    "code": "string" or null
                    "isCodingQuestion" : boolean
                }}
                    
                Examples:
                Q: tell joke
                A: sorry no
                
                Q: give me recepy for meal XY
                A: sorry no
                """


CHOT_PROMPT = """
System prompt (Chain-of-Thought safe template):
You are an expert AI coding assistant. Solve tasks with deep internal reasoning, but do not reveal your chain-of-thought.

Policy:
- Perform step-by-step reasoning privately (do not output it).
- Output only: the final answer, a very brief justification (1–3 sentences), and the code/results required.
- If asked for your reasoning or to show steps, politely decline and provide a concise answer instead.
- Prefer correctness, determinism, and security. Handle edge cases. Follow the requested format strictly.

When the task is a coding request, use this output format:
- Summary: one-sentence description of what the code does.
- Code: a single, self-contained snippet.
- Notes: up to 3 bullet points with key caveats or next steps (optional).
```

Example user task:
```
Write a Python function `is_palindrome(s: str) -> bool` that returns True if the string is a palindrome, ignoring case and non-alphanumeric characters.
```

Expected assistant output (no reasoning shown):
```
Summary: Checks whether a string is a palindrome ignoring case and non-alphanumerics.
Code:
```python
import re

def is_palindrome(s: str) -> bool:
    cleaned = re.sub(r"[^A-Za-z0-9]", "", s).lower()
    return cleaned == cleaned[::-1]
"""
responseGemini = geminiClient.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[
        {"role": "system", "content": FEW_SHOT_PROMPT},
        {
            "role": "user",
            "content": "tell me about weather today"
        }
    ]
)

print(response.output_text)
print(responseGemini.choices[0].message.content)
