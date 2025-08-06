from typing_extensions import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from langsmith.wrappers import wrap_openai
from openai import OpenAI
from pydantic import BaseModel

class DetectedCallRespose(BaseModel):
  is_question_code: bool

class CodingAIRespose(BaseModel):
  answer: str

client = wrap_openai(OpenAI())


class State(TypedDict):
  user_message:str
  ai_msg: str
  is_coding_question: bool


def detect_query(state: State):
  user_msg = state.get("user_message")

  SYSTEM_PROMPT = """
     You are an AI assistant.
     your job is to detect if the users query is related coding question or not. 
     return the resonse in specified JSON boolean only.
  """
  #OpenAI called
  result = client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    response_format=DetectedCallRespose,
    messages=[
      {"role" : "system", "content": SYSTEM_PROMPT},
      {"role" : "user", "content": user_msg}
    ]
  )
  print(result.choices[0].message.parsed)
  state["is_coding_question"] = result.choices[0].message.parsed.is_question_code
  return state

def route_edge(state: State) -> Literal["solve_coding_question", "solve_simple_question"]:
  is_coding_question = state.get("is_coding_question")

  if is_coding_question:
    return "solve_coding_question"
  else :
    return "solve_simple_question"

def solve_coding_question(state: State):
  user_msg = state.get("user_message")

  #OpenAI called(sovle coding question using 4.1)
  SYSTEM_PROMPT = """
     You are an AI assistant.
     your job is to solve users query
  """
  #OpenAI called
  result = client.beta.chat.completions.parse(
    model="gpt-4.1",
    response_format=CodingAIRespose,
    messages=[
      {"role" : "system", "content": SYSTEM_PROMPT},
      {"role" : "user", "content": user_msg}
    ]
  )

  state["ai_msg"] = result.choices[0].message.parsed.answer
  return state


def solve_simple_question(state: State):
  user_msg = state.get("user_message")

  #OpenAI called(sovle coding question using mini model)
  SYSTEM_PROMPT = """
     You are an AI assistant.
     your job is to solve users query
  """
  #OpenAI called
  result = client.beta.chat.completions.parse(
    model="gpt-4.1",
    response_format=CodingAIRespose,
    messages=[
      {"role" : "system", "content": SYSTEM_PROMPT},
      {"role" : "user", "content": user_msg}
    ]
  )

  state["ai_msg"] = result.choices[0].message.parsed.answer

  return state


graph_builder = StateGraph(State)

graph_builder.add_node("detect_query", detect_query)
graph_builder.add_node("route_edge", route_edge)
graph_builder.add_node("solve_coding_question", solve_coding_question)
graph_builder.add_node("solve_simple_question", solve_simple_question)

graph_builder.add_edge(START, "detect_query")
graph_builder.add_conditional_edges("detect_query", route_edge)
# graph_builder.add_conditional_edges("route_edge", "solve_coding_question")
# graph_builder.add_conditional_edges("route_edge", "solve_simple_question")
graph_builder.add_edge("solve_coding_question", END)
graph_builder.add_edge("solve_simple_question", END)

graph = graph_builder.compile()

# use graph

def call_graph():
  state = {
    "user_message": "who is amy hawart",
    "ai_msg": "",
    "is_coding_question": False
  }
  result = graph.invoke(state)
  print("Final Result: ", result)


call_graph()