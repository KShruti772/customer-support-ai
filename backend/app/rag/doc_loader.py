from __future__ import annotations
import os
from typing import Dict, List

from pypdf import PdfReader


class Document:
    def __init__(self, doc_id: str, text: str, metadata: Dict = None):
        self.doc_id = doc_id
        self.text = text
        self.metadata = metadata or {}


def load_document(path: str) -> Document:
    """Load a document from path and return a Document with extracted text and metadata.

    Supports PDF, .txt, .md. Raises FileNotFoundError for missing files and ValueError for unsupported types.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Document not found: {path}")

    _, ext = os.path.splitext(path.lower())
    if ext == ".pdf":
        try:
            reader = PdfReader(path)
            texts: List[str] = []
            for page in reader.pages:
                texts.append(page.extract_text() or "")
            full_text = "\n".join(texts)
        except Exception as e:
            raise ValueError(f"Failed to extract PDF: {e}")
    elif ext in (".txt", ".md"):
        with open(path, "r", encoding="utf-8") as f:
            full_text = f.read()
    else:
        raise ValueError(f"Unsupported document type: {ext}")

    metadata = {"source_path": path, "file_ext": ext}
    return Document(doc_id=os.path.basename(path), text=full_text, metadata=metadata)


def load_documents_from_folder(folder: str, extensions=None) -> List[Document]:
    extensions = extensions or [".pdf", ".txt", ".md"]
    docs: List[Document] = []
    for root, _, files in os.walk(folder):
        for name in files:
            if os.path.splitext(name)[1].lower() in extensions:
                path = os.path.join(root, name)
                try:
                    docs.append(load_document(path))
                except Exception:
                    # skip problematic files but continue processing
                    continue
    return docs
