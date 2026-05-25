"""Build LLM prompts by injecting retrieved context into templates."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from src.rag.retriever import RetrievalResult

_PROJECT_ROOT = Path(__file__).resolve().parent.parent

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
    conflict_aware: bool = False,
    max_chunks: int | None = None,
) -> list[dict[str, str]]:
    """Build a chat-style message list for the generator.

    Returns a list of {"role": ..., "content": ...} dicts compatible
    with HuggingFace chat templates and OpenAI-style APIs.
    """
    context_str = format_context(results, max_chunks)

    system = CONFLICT_AWARE_SYSTEM if conflict_aware else BASE_SYSTEM
    template = CONFLICT_AWARE_USER_TEMPLATE if conflict_aware else USER_TEMPLATE

    user_content = template.format(
        retrieved_context=context_str,
        question=question,
    )

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user_content},
    ]
