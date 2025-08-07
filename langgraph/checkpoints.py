from typing_extensions import TypedDict, Literal
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.mongodb import MongoDBSaver


llm = init_chat_model(model_provider="openai", model="gpt-4.1")

DB_URI = "localhost:27017"
config = { "configurable": { "thread_id": "1" } }

class State(TypedDict):
  messages: Annotated[list, add_messages]

def chatbot(state: State):
  messages = state.get("messages")
  response = llm.invoke(messages)
  return {"messages": [response]}


graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)


# graph = graph_builder.compile()

def create_chat_graph(checkpointer):
  return graph_builder.compile(checkpointer=checkpointer)


def init():
  with MongoDBSaver.from_conn_string(DB_URI) as checkpointer:
    graph_with_mongo = create_chat_graph(checkpointer=checkpointer)

    while True:
      user_input = input("> ")
      # result = graph.invoke({"messages": [{"role": "user", "content": user_input}]})
      for event in graph_with_mongo.stream({"messages": [{"role": "user", "content": user_input}]}, config, stream_mode="values"):
        if "messages" in event:
          event["messages"][-1].pretty_print()


init()