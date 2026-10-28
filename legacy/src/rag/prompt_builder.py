"""Build LLM prompts by injecting retrieved context into templates."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from src.rag.config import resolve_path
from src.rag.retriever import RetrievalResult

# Fallback templates when no prompt_file is configured (tests / minimal runs).
BASE_SYSTEM = (
    "You are a helpful assistant. Answer the user's question using the "
    "provided context when it is relevant. If the context does not contain "
    "enough information, say what is missing briefly."
)

CONFLICT_AWARE_SYSTEM = (
    "You are a careful RAG assistant. Retrieved documents may conflict with "
    "facts you learned during training. Your job is to resolve such "
    "context–memory conflicts using evidence, time, conditions, and source "
    "information—not to blend incompatible claims without explanation."
)

USER_TEMPLATE = (
    "Context:\n{retrieved_context}\n\n"
    "Question:\n{question}\n\n"
    "Instructions:\n"
    "- Use the context above when it supports your answer.\n"
    "- Cite passage ids or source labels from the context when you rely on them.\n"
    "- If context and your general knowledge disagree, state uncertainty if needed."
)

CONFLICT_AWARE_USER_TEMPLATE = (
    "Context (retrieved evidence; each block has a source label):\n"
    "{retrieved_context}\n\n"
    "Question:\n{question}\n\n"
    "Instructions:\n"
    "1. Check whether any context passage contradicts what you would answer from memory alone.\n"
    "2. If there is a conflict:\n"
    "   - State that a conflict exists between retrieved evidence and internal knowledge.\n"
    "   - Prefer retrieved evidence when it is authoritative, specific, and time-valid.\n"
    "   - Prefer internal knowledge when retrieved evidence is vague, outdated, or from an untrusted source.\n"
    "   - If neither source is reliable enough, abstain or explain uncertainty explicitly.\n"
    "3. When answering, mention which source you followed and relevant source labels."
)


@dataclass(frozen=True)
class PromptTemplate:
    """System message and user message template loaded from configs/prompts/*.md."""

    system: str
    user_template: str


def _extract_section(body: str, heading: str) -> str:
    """Return text under a ``## heading`` until the next ``##`` heading."""
    pattern = rf"^##\s+{re.escape(heading)}\s*\n(.*?)(?=^##\s|\Z)"
    match = re.search(pattern, body, flags=re.MULTILINE | re.DOTALL | re.IGNORECASE)
    if not match:
        raise ValueError(f"Missing '## {heading}' section in prompt file")
    return match.group(1).strip()


def _strip_fenced_block(text: str) -> str:
    """Unwrap a single markdown fenced code block if present."""
    text = text.strip()
    fence = re.match(r"^```(?:\w+)?\s*\n(.*)\n```\s*$", text, flags=re.DOTALL)
    if fence:
        return fence.group(1).strip()
    return text


def load_prompt_template(prompt_path: str | Path) -> PromptTemplate:
    """Load system and user templates from ``configs/prompts/*.md``."""
    path = resolve_path(prompt_path)
    body = path.read_text(encoding="utf-8")
    system = _extract_section(body, "System")
    user_raw = _extract_section(body, "User template")
    user_template = _strip_fenced_block(user_raw)
    return PromptTemplate(system=system, user_template=user_template)


def default_template(conflict_aware: bool = False) -> PromptTemplate:
    """Built-in templates when ``prompt_file`` is not set in YAML."""
    if conflict_aware:
        return PromptTemplate(
            system=CONFLICT_AWARE_SYSTEM,
            user_template=CONFLICT_AWARE_USER_TEMPLATE,
        )
    return PromptTemplate(system=BASE_SYSTEM, user_template=USER_TEMPLATE)


def format_context(results: Sequence[RetrievalResult], max_chunks: int | None = None) -> str:
    """Format retrieval results into a numbered context string."""
    items = results[:max_chunks] if max_chunks else results
    blocks: list[str] = []
    for i, r in enumerate(items, 1):
        source_label = r.source or f"passage_{i}"
        blocks.append(f"[{source_label}]\n{r.text}")
    return "\n\n".join(blocks)


def build_prompt(
    question: str,
    results: Sequence[RetrievalResult],
    template: PromptTemplate | None = None,
    conflict_aware: bool = False,
    max_chunks: int | None = None,
) -> list[dict[str, str]]:
    """Build a chat-style message list for the generator.

    Returns a list of {"role": ..., "content": ...} dicts compatible
    with HuggingFace chat templates and OpenAI-style APIs.
    """
    tmpl = template or default_template(conflict_aware)
    context_str = format_context(results, max_chunks)

    user_content = tmpl.user_template.format(
        retrieved_context=context_str,
        question=question,
    )

    return [
        {"role": "system", "content": tmpl.system},
        {"role": "user", "content": user_content},
    ]
