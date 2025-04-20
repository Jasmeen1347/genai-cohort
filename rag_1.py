from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

# load document
file_path = Path(__file__).parent / "nodejs2.pdf"
loader = PyPDFLoader(file_path)
docs = loader.load()


text_spliter = RecursiveCharacterTextSplitter(
  chunk_size = 1000,
  chunk_overlap=200
)

split_doc = text_spliter.split_documents(documents=docs)

embedding = OpenAIEmbeddings(
  model="text-embedding-3-large",
  api_key="OPENAI_API"
)

# vector_store = QdrantVectorStore.from_documents(
#   documents=[],
#   collection_name="learning_langchain",
#   url="http://localhost:6333/",
#   embedding=embedding
# )

# vector_store.add_documents(documents=split_doc)

print("Injection Done")

retriver = QdrantVectorStore.from_existing_collection(
   collection_name="learning_langchain",
  url="http://localhost:6333/",
  embedding=embedding
)

search_result = retriver.similarity_search(
  query="what is fs module?"
)

# print("relavant chunks", search_result)

SYSTEM_PROMPTS=f"""
You are an helpfull AI assistent who responds base on available context.

Conted:{search_result}
"""



result = client.chat.completions.create(
  model="gpt-4o",
  messages=[
    { "role": "system", "content": SYSTEM_PROMPTS },
    {'role': "user", "content": "what is fs module?"}
  ]
)

print(result.choices[0].message.content)