from __future__ import annotations
from typing import Dict, List, Tuple
import os
import json
import faiss
import numpy as np


class FaissIndex:
    def __init__(self, dim: int, index_path: str):
        self.dim = dim
        self.index_path = index_path
        self.index = faiss.IndexFlatIP(dim)  # inner product on normalized vectors
        self._metapath = index_path + ".meta.json"
        self._metadata: List[Dict] = []

    def add(self, embeddings: List[List[float]], metadatas: List[Dict]):
        arr = np.array(embeddings, dtype="float32")
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)
        faiss.normalize_L2(arr)
        self.index.add(arr)
        self._metadata.extend(metadatas)

    def save(self):
        # persist faiss binary and metadata JSON
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self._metapath, "w", encoding="utf-8") as f:
            json.dump(self._metadata, f, ensure_ascii=False, indent=2)

    def load(self):
        if not os.path.exists(self.index_path) or not os.path.exists(self._metapath):
            raise FileNotFoundError("Index or metadata not found")
        self.index = faiss.read_index(self.index_path)
        with open(self._metapath, "r", encoding="utf-8") as f:
            self._metadata = json.load(f)

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[Dict, float]]:
        if self.index.ntotal == 0:
            return []
        vec = np.array(query_embedding, dtype="float32").reshape(1, -1)
        faiss.normalize_L2(vec)
        D, I = self.index.search(vec, top_k)
        results: List[Tuple[Dict, float]] = []
        for score, idx in zip(D[0], I[0]):
            if idx < 0 or idx >= len(self._metadata):
                continue
            results.append((self._metadata[idx], float(score)))
        return results
