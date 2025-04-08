from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()
 

text="loem epsum is demo text that eveny developer use when they dont have any content"

response = client.embeddings.create(
  input=text,
  model="text-embedding-3-small"
)

print("vector embedding: ", response.data[0].embedding)

