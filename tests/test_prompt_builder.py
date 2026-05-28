"""Tests for prompt template loading (no torch required)."""

from src.rag.prompt_builder import load_prompt_template


def test_load_base_rag_prompt_template():
    tmpl = load_prompt_template("configs/prompts/base_rag.md")
    assert "helpful assistant" in tmpl.system.lower()
    assert "{retrieved_context}" in tmpl.user_template
    assert "{question}" in tmpl.user_template


def test_load_conflict_aware_prompt_template():
    tmpl = load_prompt_template("configs/prompts/conflict_aware.md")
    assert "context" in tmpl.system.lower() and "conflict" in tmpl.system.lower()
    assert "{retrieved_context}" in tmpl.user_template
