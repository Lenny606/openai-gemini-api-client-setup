from openai import OpenAI
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
# rq worker command
load_dotenv()

client = OpenAI()
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
db = QdrantVectorStore.from_existing_collection(url="http://localhost:6333", collection_name="test_collection",
                                                embedding=embeddings)


def process_query(q: str):
    print(f"Processing query: {q}")
    results = db.similarity_search_with_score(q, k=3)

    # context string from results
    context = "\n\n\n".join([r[0].page_content for r in results])

    SYSTEM_PROMPT = f"""You are a helpful assistant who can answer questions about the following documents with context.
        CONTEXT:
        {context}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": q}
        ]
    )
    return response.choices[0].message.content
