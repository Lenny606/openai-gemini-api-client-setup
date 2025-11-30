from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Protocol, Sequence, Tuple, Dict, Any

import math
import json
import os


@dataclass
class Document:
    """
    A simple text document with optional metadata and identifier.
    """

    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: Optional[str] = None


class Embedder(Protocol):
    """Protocol for embedding backends."""

    def embed(self, texts: Sequence[str]) -> List[List[float]]:  # pragma: no cover - protocol
        ...

    @property
    def dimension(self) -> Optional[int]:  # pragma: no cover - protocol
        ...


class OpenAIEmbedder:
    """
    OpenAI embeddings-based embedder.

    - Uses the official `openai` Python SDK.
    - Reads `OPENAI_API_KEY` from environment if client not provided.
    - Default model: `text-embedding-3-small` (1,536 dims; cost-effective).
    """

    def __init__(self, model: str = "text-embedding-3-small", client: Any = None) -> None:
        try:
            from openai import OpenAI  # type: ignore
        except Exception as e:  # pragma: no cover - import guard
            raise RuntimeError("openai package is required for OpenAIEmbedder") from e

        self._OpenAI = OpenAI
        self._client = client or OpenAI()
        self._model = model
        self._dimension: Optional[int] = None

    @property
    def model(self) -> str:
        return self._model

    @property
    def dimension(self) -> Optional[int]:
        return self._dimension

    def embed(self, texts: Sequence[str]) -> List[List[float]]:
        if not texts:
            return []
        # OpenAI embeddings API expects `input` as a list for batching.
        res = self._client.embeddings.create(model=self._model, input=list(texts))
        vectors = [d.embedding for d in res.data]
        if vectors and self._dimension is None:
            self._dimension = len(vectors[0])
        return vectors


def _cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    if not a or not b:
        return 0.0
    if len(a) != len(b):
        # Different dimensions — cannot compare meaningfully
        return 0.0
    dot = 0.0
    na = 0.0
    nb = 0.0
    for x, y in zip(a, b):
        dot += x * y
        na += x * x
        nb += y * y
    denom = math.sqrt(na) * math.sqrt(nb)
    if denom == 0:
        return 0.0
    return dot / denom


class VectorStore:
    """
    Simple in-memory vector store with text chunking and similarity search.

    Example:
        >>> from rag.vector_store import VectorStore, OpenAIEmbedder, Document
        >>> vs = VectorStore(OpenAIEmbedder())
        >>> vs.add_documents(["Hello world", "OpenAI embeddings are great!"])
        >>> results = vs.search("embeddings", k=1)
        >>> results[0][0].text  # top document text
        'OpenAI embeddings are great!'
    """

    def __init__(self, embedder: Embedder) -> None:
        self._embedder = embedder
        self._documents: List[Document] = []
        self._embeddings: List[List[float]] = []

    # --------------- Chunking ---------------
    @staticmethod
    def chunk_text(
        text: str,
        chunk_size: int = 800,
        chunk_overlap: int = 200,
        strategy: str = "words",
    ) -> List[str]:
        """
        Split text into chunks with overlap.

        - strategy="words" splits on whitespace to reduce mid-word cuts.
        - chunk_size and chunk_overlap are approximate for word strategy (by word count),
          but aim to keep chunk lengths balanced.
        """

        if chunk_size <= 0:
            raise ValueError("chunk_size must be > 0")
        if chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be >= 0 and < chunk_size")

        if not text:
            return []

        if strategy == "words":
            words = text.split()
            if not words:
                return []
            step = max(1, chunk_size - chunk_overlap)
            chunks: List[str] = []
            start = 0
            while start < len(words):
                end = min(len(words), start + chunk_size)
                chunk = " ".join(words[start:end])
                chunks.append(chunk)
                if end == len(words):
                    break
                start += step
            return chunks
        elif strategy == "chars":
            chunks = []
            start = 0
            step = chunk_size - chunk_overlap
            while start < len(text):
                end = min(len(text), start + chunk_size)
                chunks.append(text[start:end])
                if end == len(text):
                    break
                start += step
            return chunks
        else:
            raise ValueError(f"Unsupported chunking strategy: {strategy}")

    # --------------- Indexing ---------------
    def add_documents(
        self,
        docs: Iterable[Document | str],
        *,
        chunk: bool = True,
        chunk_size: int = 800,
        chunk_overlap: int = 200,
        chunk_strategy: str = "words",
        batch_size: int = 64,
        parent_id_key: str = "parent_id",
    ) -> int:
        """
        Add documents or raw strings to the store.

        - If `chunk` is True, each document will be split into chunks before embedding.
        - Returns the total number of chunks added.
        """

        # Normalize to Document objects
        normalized: List[Document] = []
        for d in docs:
            if isinstance(d, Document):
                normalized.append(d)
            else:
                normalized.append(Document(text=str(d)))

        # Prepare chunked docs
        to_index: List[Document] = []
        for d in normalized:
            if chunk:
                chunks = self.chunk_text(d.text, chunk_size, chunk_overlap, chunk_strategy)
                if not chunks:
                    continue
                for i, ch in enumerate(chunks):
                    meta = dict(d.metadata) if d.metadata else {}
                    if d.id:
                        meta[parent_id_key] = d.id
                    chunk_id = f"{d.id or 'doc'}:{i}"
                    to_index.append(Document(text=ch, metadata=meta, id=chunk_id))
            else:
                to_index.append(d)

        # Embed in batches
        total_added = 0
        i = 0
        while i < len(to_index):
            batch = to_index[i : i + batch_size]
            vectors = self._embedder.embed([b.text for b in batch])
            self._documents.extend(batch)
            self._embeddings.extend(vectors)
            total_added += len(batch)
            i += batch_size
        return total_added

    # --------------- Search ---------------
    def search(self, query: str, k: int = 5) -> List[Tuple[Document, float]]:
        """Return top-k documents with cosine similarity scores."""
        if not self._documents:
            return []
        qv = self._embedder.embed([query])[0]
        scored: List[Tuple[int, float]] = []
        for idx, v in enumerate(self._embeddings):
            scored.append((idx, _cosine_similarity(qv, v)))
        scored.sort(key=lambda x: x[1], reverse=True)
        top = scored[: max(0, k)]
        return [(self._documents[i], score) for i, score in top]

    # --------------- Maintenance ---------------
    def clear(self) -> None:
        self._documents.clear()
        self._embeddings.clear()

    # --------------- Persistence ---------------
    def save(self, path: str) -> None:
        if not path:
            raise ValueError("path is required")
        data = {
            "embedder": {
                "type": self._embedder.__class__.__name__,
                # Saving the model may help ensure compatibility when reloading
                **({"model": getattr(self._embedder, "model", None)}),
            },
            "items": [
                {
                    "document": {
                        "text": d.text,
                        "metadata": d.metadata,
                        "id": d.id,
                    },
                    "embedding": emb,
                }
                for d, emb in zip(self._documents, self._embeddings)
            ],
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

    @classmethod
    def load(cls, path: str, embedder: Embedder) -> "VectorStore":
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        vs = cls(embedder)
        items = data.get("items", [])
        for item in items:
            doc = item.get("document", {})
            d = Document(text=doc.get("text", ""), metadata=doc.get("metadata", {}), id=doc.get("id"))
            emb = item.get("embedding", [])
            if d.text and emb:
                vs._documents.append(d)
                vs._embeddings.append(list(emb))
        return vs
