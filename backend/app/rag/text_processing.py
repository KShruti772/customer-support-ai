from __future__ import annotations
from typing import List
from langchain_text_splitters import CharacterTextSplitter


def clean_text(text: str) -> str:
    """Simple cleaning: normalize whitespace and remove excessive newlines."""
    if text is None:
        return ""
    # Normalize line endings and collapse multiple spaces/newlines
    cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
    # collapse repeated newlines
    while "\n\n\n" in cleaned:
        cleaned = cleaned.replace("\n\n\n", "\n\n")
    return cleaned.strip()


def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """Split text into chunks using LangChain's CharacterTextSplitter.

    chunk_size and chunk_overlap are configurable.
    """
    splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    return splitter.split_text(text)
