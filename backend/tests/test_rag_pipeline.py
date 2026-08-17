import os
import shutil
import tempfile

import pytest

from backend.app.rag.pipeline import RAGPipeline
from backend.app.rag.doc_loader import load_document


def create_sample_txt(path: str, content: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def test_document_loading_and_missing():
    tmp = tempfile.mkdtemp()
    try:
        p = os.path.join(tmp, "doc1.txt")
        create_sample_txt(p, "Hello world\nThis is AstraHome FAQ content about cameras.")
        doc = load_document(p)
        assert "AstraHome" in doc.text
        with pytest.raises(FileNotFoundError):
            load_document(os.path.join(tmp, "nope.pdf"))
    finally:
        shutil.rmtree(tmp)


def test_chunking_and_embedding_and_search(tmp_path):
    # create simple docs
    data_dir = tmp_path / "docs"
    data_dir.mkdir()
    f1 = data_dir / "faq.txt"
    f1.write_text("AstraHome camera warranty is one year. Returns within 30 days for unopened items.")
    f2 = data_dir / "shipping.txt"
    f2.write_text("Standard shipping 3-5 business days. Expedited 1-2 days. Free shipping over $75.")

    index_path = str(tmp_path / "faiss.index")
    # use dummy embeddings for fast deterministic tests
    pipeline = RAGPipeline(source_folder=str(data_dir), index_path=index_path, embedding_model_name="dummy", chunk_size=50, chunk_overlap=10)
    pipeline.build_index(rebuild=True)

    # relevant query
    hits = pipeline.semantic_search("How long is the warranty?", top_k=3)
    assert isinstance(hits, list)
    # expect at least one result that references 'warranty'
    assert any("warranty" in (h["metadata"]["text"]).lower() for h in hits)

    # irrelevant query
    hits2 = pipeline.semantic_search("How to cook pasta?", top_k=3)
    # dummy embedding may still return results but scores should be low or texts unrelated
    assert isinstance(hits2, list)

    # empty query
    empty = pipeline.semantic_search("   ", top_k=3)
    assert empty == []


def test_persist_and_load(tmp_path):
    data_dir = tmp_path / "docs2"
    data_dir.mkdir()
    (data_dir / "p.txt").write_text("This device supports 2.4GHz Wi-Fi only.")
    index_path = str(tmp_path / "faiss2.index")
    p = RAGPipeline(source_folder=str(data_dir), index_path=index_path, embedding_model_name="dummy", chunk_size=50, chunk_overlap=5)
    p.build_index(rebuild=True)
    # ensure files exist
    assert os.path.exists(index_path)
    assert os.path.exists(index_path + ".meta.json")

    # load without rebuilding
    p2 = RAGPipeline(source_folder=str(data_dir), index_path=index_path, embedding_model_name="dummy")
    p2.build_index(rebuild=False)
    res = p2.semantic_search("5GHz?", top_k=2)
    assert isinstance(res, list)
