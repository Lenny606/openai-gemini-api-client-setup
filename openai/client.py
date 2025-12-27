from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
gemini_key = os.getenv("GEMINI_API_KEY")

# client = OpenAI()
# response = client.responses.create(
#     model="gpt-4o-mini",
#     input="What day is today?"
# )
# print(response.output_text)

# gemini compatible
geminiClient = OpenAI(
    api_key=gemini_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# Prompt templates

# Zero-shot prompt: minimal instruction-only guardrails
ZERO_SHOT_PROMPT = (
    "Answer only coding questions with code. If the request is not about programming, reply: 'sorry, no'."
)

# Few-shot prompt: adds format rules and examples for stricter behavior
FEW_SHOT_PROMPT = """
You are a coding-only assistant.
Rules:
- If the request is not about programming, reply exactly: "sorry, no".
- When it is a coding request, reply in JSON using the schema below.

Output JSON schema:
{
  "code": string | null,
  "isCodingQuestion": boolean
}

Examples:
Q: tell a joke
A: {"code": null, "isCodingQuestion": false}

Q: give me recipe for meal XY
A: {"code": null, "isCodingQuestion": false}

Q: write a Python function that returns the square of a number
A: {"code": "def square(x: int) -> int:\n    return x * x", "isCodingQuestion": true}
"""

from typing import Literal

# Persona prompt: prepend to zero/few-shot to steer tone/role
PERSONA_PROMPT = """
Persona: {role}
Tone: {tone}
Audience: {audience}

Guidance:
- Keep responses concise and professional.
- Prefer deterministic, safe solutions.
- If constraints conflict, prioritize correctness over style.
"""

CHAIN_OF_THOUGHT_PROMPT = """
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
PromptMode = Literal["zero", "few", "cot"]

def build_system_prompt(mode: PromptMode, role: str, tone: str, audience: str) -> str:
    persona = PERSONA_PROMPT.format(role=role, tone=tone, audience=audience).strip()
    if mode == "zero":
        return f"{persona}\n\n{ZERO_SHOT_PROMPT}"
    if mode == "few":
        return f"{persona}\n\n{FEW_SHOT_PROMPT}"
    # default to CoT safe policy
    return f"{persona}\n\n{CHAIN_OF_THOUGHT_PROMPT}"


# Config via environment variables with sensible defaults
PROMPT_MODE: PromptMode = os.getenv("PROMPT_MODE", "zero").lower()  # zero|few|cot
PERSONA_ROLE = os.getenv("PERSONA_ROLE", "Senior Python library maintainer")
PERSONA_TONE = os.getenv("PERSONA_TONE", "concise, professional")
PERSONA_AUDIENCE = os.getenv("PERSONA_AUDIENCE", "intermediate developers")

system_prompt = build_system_prompt(PROMPT_MODE, PERSONA_ROLE, PERSONA_TONE, PERSONA_AUDIENCE)

message_history = [
    {"role": "system", "content": system_prompt}
]

# add history
user_query = input("Enter: ")
message_history.append({"role": "user", "content": user_query})

while True:
    responseGemini = geminiClient.chat.completions.create(
        model="gemini-2.5-flash",
        messages=message_history
    )

    raw_output = responseGemini.choices[0].message.content
    message_history.append({"role": "assistant", "content": raw_output})

    print(raw_output)
