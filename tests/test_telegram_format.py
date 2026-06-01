"""Tests for Telegram HTML formatting (no telegram/network required)."""

from src.chatbot.telegram_format import (
    build_about_blurb,
    format_for_telegram_html,
    format_where_hit,
    to_plain_fallback,
)


def test_format_bold_and_code():
    out = format_for_telegram_html("**RAG** and `src/rag/pipeline.py`")
    assert "<b>RAG</b>" in out
    assert "<code>src/rag/pipeline.py</code>" in out
    assert "**" not in out


def test_format_code_span_with_inner_backticks_stripped_in_where():
    line = format_where_hit("src/a.py", 10, "x = `value`")
    html = format_for_telegram_html(line)
    assert "<code>src/a.py:10</code>" in html
    assert "`value`" not in html or "value" in html


def test_format_escapes_angle_brackets():
    out = format_for_telegram_html("if a < b and c > d")
    assert "&lt;" in out
    assert "<b>" not in out.replace("&lt;", "")


def test_build_about_blurb_skips_tables_and_badges():
    raw = """
<div>
[![badge](https://img.shields.io/badge/x-y-blue?style=for-the-badge)](http://x)
# Title
| a | b |
|---|---|
**Bold line**
"""
    blurb = build_about_blurb(raw, max_chars=500)
    assert "img.shields.io" not in blurb
    assert "| a |" not in blurb
    assert "Bold line" in blurb or "<b>" in format_for_telegram_html(blurb)


def test_plain_fallback_strips_tags():
    raw = "**hello** `code`"
    plain = to_plain_fallback(raw)
    assert "<" not in plain
    assert "hello" in plain
