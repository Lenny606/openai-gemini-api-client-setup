from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

gpt_model = "gpt-4o-mini"
ollama_model = "llama3.2:1b"
local_url = "http://localhost:11434/v1"

gpt_client = OpenAI()
ollama_client = OpenAI(
    api_key="ollama",
    base_url=local_url
)
gemini_client = OpenAI(
    api_key= os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

gpt_system_m = "You are very argumentative chatbot. Mostly disagree with everything, challeging all"
local_system_m = "You are very polite chatbot.Nicely explaining all questions, but not overly verbose, strict and short"
gemini_system_m = "You are 3rd user in conversation between two users. React on conversations with insides"

gpt_user_m = ["Hi, what your though about solving racism"]
local_user_m = ["Hello"]


def call_gpt():
    messages = [{
        "role": "system",
        "content": gpt_system_m
    }]
    for gpt, local in zip(gpt_user_m,local_user_m):
        messages.append({"role": "assistant", "content": gpt})
        messages.append({"role": "user", "content": local})

    r = gpt_client.chat.completions.create(model=gpt_model,messages=messages)
    return r.choices[0].message.content

def call_local():
    messages = [{
        "role": "system",
        "content": local_system_m
    }]
    for gpt, local in zip(gpt_user_m,local_user_m):
        messages.append({"role": "assistant", "content": gpt})
        messages.append({"role": "user", "content": local})
    messages.append({"role": "user", "content": gpt_user_m[-1]})
    r = ollama_client.chat.completions.create(model=ollama_model, messages= messages)
    return r.choices[0].message.content

def call_gemini():
    conversation = zip(gpt_user_m, local_user_m)
    messages = [{
        "role": "system",
        "content": gemini_system_m
    }]

    for gpt, local in conversation:
        messages.append({"role": "assistant", "content": gpt})
        messages.append({"role": "assistant", "content": local})

    gemini_user_m = f""" 
    You are in conversation between two users. Convarsations: {messages}
    """
    messages.append({"role": "user", "content": gemini_user_m})
    r = gemini_client.chat.completions.create(model="gemini-2.5-flash", messages=messages)
    return r.choices[0].message.content

for i in range(5):
    gpt_next = call_gpt()
    print("GPT: "  + gpt_next)
    gpt_user_m.append(gpt_next)

    local_next = call_local()
    print("LOCAL " + local_next)
    local_user_m.append(local_next)

    gemini_next = call_gemini()
    print("GEMINI: " + gemini_next)