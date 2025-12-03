from langchain_classic.chat_models import init_chat_model
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from typing import Annotated
from dotenv import load_dotenv
load_dotenv()

llm = init_chat_model(
    model="gpt-4o-mini",
    model_provider="openai"
)

# create State from TD with metadata List
class State(TypedDict):
    messages: Annotated[list, add_messages]


def chat(state: State):
    res = llm.invoke(state.get("messages"))
    return {
        "messages": [res]
    }


def second_node(state: State):
    return (
        {"messages": ["second_node"]}
    )


# build graph
graph_builder = StateGraph(State)
graph_builder.add_node("chat", chat)
graph_builder.add_node("second", second_node)

graph_builder.add_edge(START, "chat")
graph_builder.add_edge("chat", "second")
graph_builder.add_edge("second", END)

graph = graph_builder.compile()
# start with initial state as Dict with ann list
r = graph.invoke(State({
    "messages": ["Hello"]
}))

print(r)