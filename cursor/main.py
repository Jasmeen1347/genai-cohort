import json

from dotenv import load_dotenv
from openai import OpenAI
import os

# load_dotenv()

# api_key = os.getenv("GEMINI_API_KEY")

client = OpenAI(
  api_key="",
  base_url="https://generativelanguage.googleapis.com/v1beta/openai"
)

def run_command(command):
  result = os.system(command=command)
  return result

avaiable_tools = {
    "run_command": {
        "fn": run_command,
        "description": "Takes a command as input to execute on system and returns ouput"
    }
}

system_prompt = """
    You are an helpfull AI Assistant who is specialized in nodejs development.
    You work on start, plan, action, observe mode.
    For the given user query and available tools, plan the step by step execution, based on the planning,
    select the relevant tool from the available tool. and based on the tool selection you perform an action to call the tool.
    Wait for the observation and based on the observation from the tool call resolve the user query.
    Whenever you create new project youhave to create main folder inside that folder you have to write modular code like conroller, services, db connection and others required code files in that folders.
    os running in this device is windows os
    all the code you create/write should go inside main folder.


    Rules:
    - Follow the Output JSON Format.
    - Always perform one step at a time and wait for next input
    - Carefully analyse the user query
    - Write modular code
    - Code must be easy to understand
    - Use JWT for authentication

    Output JSON Format:
    {{
        "step": "string",
        "content": "string",
        "function": "The name of function if the step is action",
        "input": "The input parameter for the function",
    }}

    Available Tools:
    - run_command: Takes a command as input to execute on system and returns ouput
    
    Example:
    User Query: What is the weather of new york?
    Output: {{ "step": "plan", "content": "The user is interseted in weather data of new york" }}
    Output: {{ "step": "plan", "content": "From the available tools I should call run_command" }}
    Output: {{ "step": "action", "function": "run_command", "input": "new york" }}
    Output: {{ "step": "observe", "output": "12 Degree Cel" }}
    Output: {{ "step": "output", "content": "The weather for new york seems to be 12 degrees." }}

"""


messages = [
    { "role": "system", "content": system_prompt }
]


while True:
  user_query = input("> ")

  while True:
    messages.append({"role": "user", "content": user_query})
    response = client.chat.completions.create(
      model="gemini-2.0-flash",
      response_format={"type": "json_object"},
      messages=messages
    )
    parsed_output = json.loads(response.choices[0].message.content)
    messages.append({"role": "assistant", "content": json.dumps(parsed_output)})

    if parsed_output.get("step") == "plan":
      print(f"think: {parsed_output.get('content')}")
      continue

    if parsed_output.get("step") == "action":
      tool_name = parsed_output.get("function")
      tool_input = parsed_output.get("input")

      if avaiable_tools.get(tool_name, False) != False:
        output = avaiable_tools[tool_name].get("fn")(tool_input)
        messages.append({"role": "assistant", "content": json.dumps({"step": "observ", "output": output})})
        continue

    if parsed_output.get("step") == "output":
      print(f"output: {parsed_output.get('content')}")
      break

