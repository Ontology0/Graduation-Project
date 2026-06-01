"""Telegram HTML formatting helpers (parse_mode=HTML safe)."""

from __future__ import annotations

import re
from html import escape as html_escape

# Telegram HTML allows a small tag subset; keep conversions conservative.
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_HEADER_RE = re.compile(r"^#{1,6}\s+", re.MULTILINE)
_FENCE_RE = re.compile(r"```[\w]*\n?([\s\S]*?)```")
_TABLE_LINE_RE = re.compile(r"^\s*\|.+\|\s*$", re.MULTILINE)


def strip_html_tags(text: str) -> str:
    """Remove HTML tags and collapse excessive blank lines."""
    s = re.sub(r"<[^>]+>", "", text or "")
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def _strip_markdown_noise(text: str) -> str:
    """Remove markdown constructs that Telegram HTML mode cannot render reliably."""
    s = text or ""
    s = _FENCE_RE.sub(lambda m: (m.group(1) or "").strip(), s)
    s = _TABLE_LINE_RE.sub("", s)
    s = _LINK_RE.sub(r"\1 (\2)", s)
    s = _HEADER_RE.sub("", s)
    # Lone *italic* (single asterisks) — drop markers, keep text
    s = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"\1", s)
    return s


def format_for_telegram_html(text: str) -> str:
    """Convert a small markdown subset to Telegram HTML safely.

    Supported outside code spans:
    - **bold** -> <b>bold</b>
  - `code` -> <code>code</code>

    All other text is HTML-escaped. Code spans are split first so inner
    backticks or ** do not break the parser.
    """
    s = _strip_markdown_noise((text or "").strip())
    if not s:
        return s

    parts = re.split(r"`([^`]*)`", s)
    out: list[str] = []
    for i, part in enumerate(parts):
        if i % 2 == 1:
            out.append(f"<code>{html_escape(part, quote=False)}</code>")
            continue
        chunk = html_escape(part, quote=False)
        chunk = re.sub(r"\*\*([^*\n]+)\*\*", r"<b>\1</b>", chunk)
        out.append(chunk)
    return "".join(out)


def format_where_hit(path: str, line: int, snippet: str) -> str:
    """One grep hit as markdown-ish text (pass through format_for_telegram_html)."""
    loc = f"{path}:{line}"
    body = (snippet or "").strip().replace("`", "'")[:400]
    return f"- `{loc}`\n  {body}"


def build_about_blurb(readme_text: str, *, max_chars: int = 3200) -> str:
    """Short project intro for /about (not the full README)."""
    lines_out: list[str] = []
    for raw in strip_html_tags(readme_text).splitlines():
        line = raw.strip()
        if not line:
            if lines_out and lines_out[-1] != "":
                lines_out.append("")
            continue
        if line.startswith("|"):
            continue
        if line.startswith("!["):
            continue
        if "img.shields.io" in line or "style=for-the-badge" in line:
            continue
        line = _HEADER_RE.sub("", line).strip()
        if not line:
            continue
        lines_out.append(line)
        if sum(len(x) + 1 for x in lines_out) >= max_chars:
            break

    blurb = "\n".join(lines_out).strip()
    if len(blurb) > max_chars:
        blurb = blurb[: max_chars - 3].rstrip() + "..."
    if not blurb:
        return "프로젝트 소개를 불러오지 못했어."
    blurb += "\n\n(전체 README는 GitHub 저장소를 참고)"
    return blurb


def to_plain_fallback(text: str) -> str:
    """Strip our HTML tags for parse_mode=None fallback."""
    s = strip_html_tags(format_for_telegram_html(text))
    return s or (text or "").strip()
