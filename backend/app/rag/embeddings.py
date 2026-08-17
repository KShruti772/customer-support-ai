from __future__ import annotations
from typing import Iterable, List
import numpy as np


class EmbeddingModel:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    def _load_model(self):
        if self.model_name == "dummy":
            self._model = None
            return
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(self.model_name)

    def embed(self, texts: Iterable[str]) -> List[List[float]]:
        """Return list of embeddings for given texts. """
        if self._model is None and self.model_name != "dummy":
            self._load_model()

        if self.model_name == "dummy":
            # deterministic pseudo-embeddings for testing
            def to_vec(s: str):
                a = np.frombuffer(s.encode("utf-8"), dtype=np.uint8)
                # reduce or pad to 128 dims
                vec = np.zeros(128, dtype=float)
                n = min(len(a), 128)
                if n > 0:
                    vec[:n] = a[:n]
                # normalize
                norm = np.linalg.norm(vec)
                if norm == 0:
                    return vec.tolist()
                return (vec / norm).tolist()

            return [to_vec(t) for t in texts]

        embeddings = self._model.encode(list(texts), convert_to_numpy=True)
        # normalize vectors to unit length for cosine similarity via inner product
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        embeddings = embeddings / norms
        return embeddings.tolist()
