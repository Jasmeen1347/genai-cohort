import os
from transformers import AutoTokenizer
from transformers import AutoModelForCausalLM
from transformers import pipeline
from dotenv import load_dotenv

load_dotenv()

model_name="google/gemma-3-1b-it"

tokenizer = AutoTokenizer.from_pretrained(model_name) 

input_tokens = tokenizer("Hello World")["input_ids"] 
# print(input_tokens)

model = AutoModelForCausalLM.from_pretrained(model_name)


genpipeline = pipeline("text-generation", model=model, tokenizer=tokenizer)

genpipeline("Hey there", max_new_tokens=25)