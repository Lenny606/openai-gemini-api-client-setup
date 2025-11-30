"""
Lightweight Retrieval and Embedding utilities.

This package provides a simple in-memory vector store with text chunking,
embedding, and similarity search capabilities. It is dependency-light and
integrates with OpenAI embeddings by default.
"""

from .vector_store import Embedder, OpenAIEmbedder, Document, VectorStore

__all__ = ["Embedder", "OpenAIEmbedder", "Document", "VectorStore"]
