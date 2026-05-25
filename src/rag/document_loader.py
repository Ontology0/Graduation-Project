"""Load raw documents from various file formats into a unified structure."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Document:
    """A single document with text content and metadata."""

    text: str
    source: str = ""
    metadata: dict = field(default_factory=dict)

    @property
    def id(self) -> str:
        return self.metadata.get("id", self.source)


def load_text_file(path: str | Path) -> Document:
    """Load a plain-text file as a single Document."""
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    return Document(text=text, source=str(path.name))


def load_json_file(path: str | Path) -> list[Document]:
    """Load a JSON file containing a list of document objects.

    Expected format: a JSON array of objects, each with at least a "text" field.
    Optional fields: "source", "metadata", and any extras stored in metadata.
    """
    path = Path(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        data = [data]

    docs: list[Document] = []
    for i, entry in enumerate(data):
        text = entry.get("text", entry.get("content", ""))
        source = entry.get("source", f"{path.name}#doc{i}")
        meta = entry.get("metadata", {})
        for key in entry:
            if key not in ("text", "content", "source", "metadata"):
                meta[key] = entry[key]
        docs.append(Document(text=text, source=source, metadata=meta))
    return docs


def load_jsonl_file(path: str | Path) -> list[Document]:
    """Load a JSONL file (one JSON object per line)."""
    path = Path(path)
    docs: list[Document] = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            text = entry.get("text", entry.get("content", ""))
            source = entry.get("source", f"{path.name}#line{i}")
            meta = entry.get("metadata", {})
            docs.append(Document(text=text, source=source, metadata=meta))
    return docs


_LOADER_MAP = {
    ".txt": lambda p: [load_text_file(p)],
    ".md": lambda p: [load_text_file(p)],
    ".json": load_json_file,
    ".jsonl": load_jsonl_file,
}


def load_documents(path: str | Path) -> list[Document]:
    """Auto-detect format and load documents from a file or directory.

    Supported formats: .txt, .md, .json, .jsonl
    If *path* is a directory, all supported files inside are loaded recursively.
    """
    path = Path(path)

    if path.is_dir():
        docs: list[Document] = []
        for ext in _LOADER_MAP:
            for file in sorted(path.rglob(f"*{ext}")):
                docs.extend(load_documents(file))
        return docs

    loader = _LOADER_MAP.get(path.suffix.lower())
    if loader is None:
        raise ValueError(f"Unsupported file format: {path.suffix}")
    return loader(path)
