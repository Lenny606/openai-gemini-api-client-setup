from pdf_loader import PDFLoader
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv

load_dotenv()

path = Path(__file__).parent / "return_label_uk_2025.pdf"

loader = PDFLoader(file_path=path)
pages = loader.load_pages()

# chunking
txt_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=400)
doc_chunks = txt_splitter.split_documents(pages)

# vector embedding
model_sm = "text-embedding-3-small"
model_lg = "text-embedding-3-large"
embeddings = OpenAIEmbeddings(model=model_lg)

qdrant_client = QdrantVectorStore.from_documents(
    documents=doc_chunks,
    embedding=embeddings,
    url="http://localhost:6333",
    collection_name="test_collection"
)
