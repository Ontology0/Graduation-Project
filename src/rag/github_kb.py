"""Build a lightweight knowledge base from the repository itself.

Goal: index only "public-facing" repo content (README/docs/configs/src) so the
Telegram bot can answer "what is this project / where is X / how to run".
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.rag.document_loader import Document


@dataclass(frozen=True)
class RepoKBConfig:
    include_dirs: tuple[str, ...] = ("docs", "src", "configs")
    include_files: tuple[str, ...] = ("README.md", "CLAUDE.md")
    exts: tuple[str, ...] = (".md", ".py", ".yaml", ".yml", ".txt")
    max_file_bytes: int = 512 * 1024  # 512 KB per file


def _is_hidden(path: Path) -> bool:
    return any(part.startswith(".") for part in path.parts)


def iter_repo_files(repo_root: str | Path, cfg: RepoKBConfig | None = None) -> list[Path]:
    cfg = cfg or RepoKBConfig()
    root = Path(repo_root).resolve()

    out: list[Path] = []
    for name in cfg.include_files:
        p = root / name
        if p.exists() and p.is_file():
            out.append(p)

    for d in cfg.include_dirs:
        base = root / d
        if not base.exists() or not base.is_dir():
            continue
        for p in base.rglob("*"):
            if not p.is_file():
                continue
            if _is_hidden(p.relative_to(root)):
                continue
            if p.suffix.lower() not in cfg.exts:
                continue
            try:
                if p.stat().st_size > cfg.max_file_bytes:
                    continue
            except OSError:
                continue
            out.append(p)

    # stable order
    out = sorted(set(out), key=lambda x: str(x))
    return out


def load_repo_documents(repo_root: str | Path, cfg: RepoKBConfig | None = None) -> list[Document]:
    """Load repo files as Documents. `source` is a repo-relative path."""
    cfg = cfg or RepoKBConfig()
    root = Path(repo_root).resolve()
    docs: list[Document] = []

    for p in iter_repo_files(root, cfg):
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # best-effort: skip weird encodings
            continue
        rel = str(p.relative_to(root))
        docs.append(Document(text=text, source=rel, metadata={"path": rel}))
    return docs


def grep_repo(repo_root: str | Path, query: str, *, limit: int = 12) -> list[dict[str, str | int]]:
    """Simple string search for `/where`.

    Returns list of {path, line, snippet}.
    """
    root = Path(repo_root).resolve()
    q = (query or "").strip()
    if not q:
        return []

    hits: list[dict[str, str | int]] = []
    files = iter_repo_files(root)
    for p in files:
        try:
            lines = p.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for i, line in enumerate(lines, 1):
            if q.lower() in line.lower():
                rel = str(p.relative_to(root))
                snippet = line.strip()
                hits.append({"path": rel, "line": i, "snippet": snippet})
                if len(hits) >= limit:
                    return hits
    return hits

