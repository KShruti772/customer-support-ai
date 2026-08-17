from __future__ import annotations
from typing import List, Dict, Any
import os

from .doc_loader import load_documents_from_folder, Document
from .text_processing import clean_text, chunk_text
from .embeddings import EmbeddingModel
from .faiss_index import FaissIndex


class RAGPipeline:
    def __init__(
        self,
        source_folder: str,
        index_path: str,
        embedding_model_name: str = "all-MiniLM-L6-v2",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        self.source_folder = source_folder
        self.index_path = index_path
        self.embedding_model = EmbeddingModel(model_name=embedding_model_name)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.index: FaissIndex | None = None

    def build_index(self, rebuild: bool = False) -> None:
        """Build FAISS index from documents in the source folder. If rebuild is False and index exists on disk, load it."""
        if not rebuild and os.path.exists(self.index_path) and os.path.exists(self.index_path + ".meta.json"):
            # load existing
            # We need to determine dim by loading metadata embeddings length; for safety, load with default dim 384
            # We'll override once loaded
            self.index = FaissIndex(dim=384, index_path=self.index_path)
            self.index.load()
            return

        documents = load_documents_from_folder(self.source_folder)
        chunks: List[str] = []
        metadatas: List[Dict[str, Any]] = []
        for doc in documents:
            text = clean_text(doc.text)
            if not text:
                continue
            parts = chunk_text(text, chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
            for i, p in enumerate(parts):
                chunks.append(p)
                metadatas.append({"doc_id": doc.doc_id, "chunk_index": i, **doc.metadata, "text": p})

        if not chunks:
            # create empty index
            self.index = FaissIndex(dim=1, index_path=self.index_path)
            self.index.save()
            return

        embeddings = self.embedding_model.embed(chunks)
        dim = len(embeddings[0])
        self.index = FaissIndex(dim=dim, index_path=self.index_path)
        self.index.add(embeddings, metadatas)
        self.index.save()

    def semantic_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Return top-k relevant chunks with metadata and score."""
        if not query or not query.strip():
            return []
        if self.index is None:
            # try to load existing index
            if os.path.exists(self.index_path) and os.path.exists(self.index_path + ".meta.json"):
                # load with default dim and rely on faiss to set dim
                self.index = FaissIndex(dim=384, index_path=self.index_path)
                self.index.load()
            else:
                raise RuntimeError("Index not built. Call build_index() first.")

        q_emb = self.embedding_model.embed([query])[0]
        results = self.index.search(q_emb, top_k=top_k)
        # return metadata + score
        return [{"metadata": m, "score": s} for m, s in results]
