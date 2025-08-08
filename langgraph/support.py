from typing_extensions import TypedDict, Literal
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.mongodb import MongoDBSaver
from langchain.tools import tool
from langgraph.types import interrupt
import json
from langgraph.types import Command
from langgraph.prebuilt import ToolNode, tools_condition

@tool()
def human_assistant_tool(query: str):
  """Request assistant from a human"""
  human_response = interrupt({"query": query})
  return human_response["data"]

tools = [human_assistant_tool]

llm = init_chat_model(model_provider="openai", model="gpt-4.1")
llm_with_tools = llm.bind_tools(tools=tools)

DB_URI = "localhost:27017"
config = { "configurable": { "thread_id": "4" } }

class State(TypedDict):
  messages: Annotated[list, add_messages]

def chatbot(state: State):
  message = llm_with_tools.invoke(state["messages"])
  assert len(message.tool_calls) <= 1
  return {"messages": [message]}


tool_node = ToolNode(tools=tools)

graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)

graph_builder.add_edge(START, "chatbot")

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools", "chatbot") # We missed this

graph_builder.add_edge("chatbot", END)


# graph = graph_builder.compile()

def create_chat_graph(checkpointer):
  return graph_builder.compile(checkpointer=checkpointer)


def init():
  with MongoDBSaver.from_conn_string(DB_URI) as checkpointer:
    graph_with_mongo = create_chat_graph(checkpointer=checkpointer)
    state = graph_with_mongo.get_state(config=config)
    # for message in state.values["messages"]:
    #   message.pretty_print()

    last_message = state.values["messages"][-1]
    tool_calls = last_message.additional_kwargs.get("tool_calls", [])  

    
    user_query = None

    for call in tool_calls:
        if call.get("function", {}).get("name") == "human_assistant_tool":
            args = call["function"].get("arguments", "{}")
            try:
                args_dict = json.loads(args)
                user_query = args_dict.get("query")
            except json.JSONDecodeError:
                print("Failed to decode function arguments.")
    
    print("User is Tying to Ask:", user_query)
    ans = input("Resolution > ")

    # OpenAI Call to mimic human

    resume_command = Command(resume={"data": ans})
    
    for event in graph_with_mongo.stream(resume_command, config, stream_mode="values"):
        if "messages" in event:
            event["messages"][-1].pretty_print()

init()