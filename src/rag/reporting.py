"""Utilities for saving and formatting RAG runs to outputs/."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from src.rag.config import load_env
from src.rag.pipeline import RAGResult


def _utc_ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def ensure_outputs_dir(base: str | Path = "outputs/runs") -> Path:
    load_env()
    path = Path(base)
    path.mkdir(parents=True, exist_ok=True)
    return path


def format_result_markdown(result: RAGResult) -> str:
    lines: list[str] = []
    lines.append(f"# RAG Run")
    lines.append("")
    lines.append(f"## Question")
    lines.append(result.question)
    lines.append("")
    lines.append(f"## Answer")
    lines.append(result.answer)
    lines.append("")
    lines.append("## Sources (top-k)")
    if not result.retrieved_sources:
        lines.append("- (none)")
    else:
        for s in result.retrieved_sources:
            src = s.get("source", "")
            score = s.get("score", "")
            text = (s.get("text", "") or "").replace("\n", " ").strip()
            lines.append(f"- **{src}** (score: {score}) — {text}")
    return "\n".join(lines).strip() + "\n"


def save_result(
    result: RAGResult,
    out_dir: str | Path = "outputs/runs",
    run_name: str | None = None,
) -> tuple[Path, Path]:
    out_dir_path = ensure_outputs_dir(out_dir)
    name = run_name or _utc_ts()
    json_path = out_dir_path / f"{name}.json"
    md_path = out_dir_path / f"{name}.md"

    payload = asdict(result)
    if result.generation_output is not None:
        payload["generation_output"] = asdict(result.generation_output)

    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(format_result_markdown(result), encoding="utf-8")
    return json_path, md_path

