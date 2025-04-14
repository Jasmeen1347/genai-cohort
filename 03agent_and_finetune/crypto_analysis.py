import json

from dotenv import load_dotenv
from openai import OpenAI
import requests
import os

load_dotenv()

client = OpenAI()

import requests

def get_crypto_price(chain: str, address: str):
    print("Tool called: get_crypto_price", chain, address)
    
    url = f"https://coins.llama.fi/prices/current/{chain}:{address}"
    response = requests.get(url)

    if response.status_code == 200:
        info = response.json()
        key = f"{chain}:{address}"
        
        if key in info.get('coins', {}):
            price = info['coins'][key]['price']
            return f"The price of the token at {key} is ${price:.2f}."
        else:
            return f"Price information not found for {key}."
    else:
        return f"Request failed with status code {response.status_code}."


avaiable_tools = {
    "get_crypto_price": {
        "fn": get_crypto_price,
        "description": "Takes a chain and token address as an input and returns the current price for the token"
    },
}

system_prompt = """
    You are an helpfull AI Assistant who is specialized in resolving user query.
    You work on start, plan, action, observe mode.
    For the given user query and available tools, plan the step by step execution, based on the planning,
    select the relevant tool from the available tool. and based on the tool selection you perform an action to call the tool.
    Wait for the observation and based on the observation from the tool call resolve the user query.

    Rules:
    - Follow the Output JSON Format.
    - Always perform one step at a time and wait for next input
    - Carefully analyse the user query

    Output JSON Format:
    {{
        "step": "string",
        "content": "string",
        "function": "The name of function if the step is action",
        "input": "The input parameter for the function",
    }}

    Available Tools:
    - get_crypto_price: Takes a chain and token address as an input and returns the current price for the token
    
    Example:
    User Query: What is the weather of new york?
    Output: {{ "step": "plan", "content": "The user is interseted in weather data of new york" }}
    Output: {{ "step": "plan", "content": "From the available tools I should call get_weather" }}
    Output: {{ "step": "action", "function": "get_crypto_price", "chain": "etheremu", "address": "0xdB25f211AB05b1c97D595516F45794528a807ad8" }}
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
      model="gpt-4o",
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
      tool_input_chain_name = parsed_output.get("chain")
      tool_input_address = parsed_output.get("address")

      if avaiable_tools.get(tool_name, False) != False:
        output = avaiable_tools[tool_name].get("fn")(tool_input_chain_name, tool_input_address)
        messages.append({"role": "assistant", "content": json.dumps({"step": "observ", "output": output})})
        continue

    if parsed_output.get("step") == "output":
      print(f"output: {parsed_output.get('content')}")
      break

