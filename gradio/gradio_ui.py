import gradio as gr
import os
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()

local_url = "http://localhost:11434/v1"
model = "llama3.2:1b"
ollama = OpenAI(
    api_key="ollama",
    base_url=local_url
)
chat_gpt = OpenAI()


def message_to_llm(input: str):
    system_prompt = "You are assistent"
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": input
        }
    ]
    res = ollama.chat.completions.create(model=model, messages=messages)
    return res.choices[0].message.content


def stream_to_ollama(input: str):
    system_prompt = "You are assistent"
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": input
        }
    ]
    result = ""
    res = ollama.chat.completions.create(model=model, messages=messages, stream=True)
    for chunk in res:
        result += chunk.choices[0].delta.content or ""
        yield result

    return res.choices[0].message.content

def stream_to_chatGPT(input: str):
    system_prompt = "You are assistent"
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": input
        }
    ]
    result = ""
    res = chat_gpt.chat.completions.create(model="gpt-4o-mini", messages=messages, stream=True)
    for chunk in res:
        result += chunk.choices[0].delta.content or ""
        yield result

    return res.choices[0].message.content

def print_message(text: str):
    # print(f"text: {text}")
    return message_to_llm(text)


# gr.Interface(fn=print_message, inputs="textbox", outputs="textbox", flagging_mode="never").launch(share=False, inbrowser=True)//simple inline

def stream_to_llm(input: str, model: str):
    yield ""
    if model == "Ollama":
       r =  stream_to_ollama(input)
    elif model == "ChatGPT":
        r = stream_to_chatGPT(input)
    else:
        r = stream_to_ollama(input)
    for chunk in r:
        yield chunk or ""

m_input = gr.Textbox(
    label="Input Box",
    info="enter value...",
    lines=7
)
m_output = gr.Textbox(
    label="Output Box",
    info="...",
    lines=8
)

md_output = gr.Markdown(
    label="Markdown Box",
)

selector = gr.Dropdown(
    choices=["Ollama", "ChatGPT"],
    label="Choose model",
    value="Ollama"
)

gr.Interface(
    fn=stream_to_llm,
    title="PRINT",
    inputs=[m_input, selector],
    outputs=[md_output],
    examples=[
        ["Explain how Transformer architecture works for llm", "Ollama"],
        ["Explain how Transformer architecture works for llm", "ChatGPT"]
    ],
    flagging_mode="never"
).launch()

# if __name__ == "__main__":
#     message = message_to_llm("Hello world")
#     print(message)
