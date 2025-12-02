from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# vector embedding for query
model_sm = "text-embedding-3-small"
model_lg = "text-embedding-3-large"
embeddings = OpenAIEmbeddings(model=model_lg)

vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="test_collection",
    embedding=embeddings
)

user_query = input("Enter your query: ")

# returns relevant documents chunks
results = vector_db.similarity_search_with_score(user_query, k=3)

# context string from results
context = "\n\n\n".join([r[0].page_content for r in results])

SYSTEM_PROMPT = f"""You are a helpful assistant who can answer questions about the following documents with context.
    CONTEXT:
    {context}
"""

client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query }
    ]
)
print(response.choices[0].message.content)
