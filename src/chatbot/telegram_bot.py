"""Telegram chatbot for the GitHub-as-KB RAG system.

This module contains the bot implementation. The CLI entrypoint lives in
`scripts/telegram_bot.py` (thin wrapper).
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import re
import subprocess
import time
from collections import defaultdict, deque
from html import escape as _html_escape
from pathlib import Path

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from src.rag.config import get_api_key, load_env
from src.rag.generator import AnthropicGenerator
from src.rag.github_kb import RepoKBConfig, grep_repo, load_repo_documents
from src.rag.pipeline import RAGPipeline
from src.rag.reporting import format_result_markdown, save_result

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[2]

_MAX_MESSAGE_CHARS = int(os.getenv("TELEGRAM_MAX_MESSAGE_CHARS", "3800"))

_BOT_WHAT_TEXT = (
    "이 텔레그램 봇은 GitHub 저장소의 `README.md`, `docs/`, `CLAUDE.md`를 지식베이스로 사용하고, "
    "문서를 청킹·임베딩한 뒤 벡터 검색으로 관련 문맥을 찾고, 해당 문맥을 프롬프트에 삽입하여 Claude가 "
    "답변을 생성하는 **RAG 기반 챗봇**입니다."
)


def _split_for_telegram(text: str, limit: int | None = None) -> list[str]:
    limit = int(limit or _MAX_MESSAGE_CHARS)
    s = (text or "").strip()
    if not s:
        return [""]
    if len(s) <= limit:
        return [s]

    parts: list[str] = []
    i = 0
    while i < len(s):
        j = min(i + limit, len(s))
        chunk = s[i:j]
        if j < len(s):
            nl = chunk.rfind("\n")
            if nl >= max(200, int(limit * 0.6)):
                j = i + nl + 1
                chunk = s[i:j]
        parts.append(chunk.rstrip())
        i = j
    return [p for p in parts if p]


def _format_for_telegram_html(text: str) -> str:
    """Convert a small markdown-ish subset to Telegram HTML safely.

    Supported:
    - **bold** -> <b>bold</b>
    - `code` -> <code>code</code>
    """

    s = (text or "").strip()
    if not s:
        return s

    # Escape HTML first, then inject our own safe tags.
    s = _html_escape(s, quote=False)

    # code: `...`
    s = re.sub(r"`([^`\n]+)`", r"<code>\1</code>", s)
    # bold: **...**
    s = re.sub(r"\*\*([^*\n][^*\n]*?)\*\*", r"<b>\1</b>", s)
    return s


async def _reply_long(update: Update, text: str) -> None:
    if not update.message:
        return
    parts = _split_for_telegram(text)
    for part in parts:
        # Telegram can rate-limit message sends; if that happens, wait and retry.
        try:
            await update.message.reply_text(
                _format_for_telegram_html(part),
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        except Exception as e:
            retry_after = getattr(e, "retry_after", None)
            if isinstance(retry_after, (int, float)) and retry_after > 0:
                await asyncio.sleep(float(retry_after))
                await update.message.reply_text(
                    _format_for_telegram_html(part),
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
            else:
                raise


def _parse_allowed_user_ids(raw: str | None) -> set[int] | None:
    if not raw:
        return None
    ids: set[int] = set()
    for part in raw.replace(" ", "").split(","):
        if not part:
            continue
        try:
            ids.add(int(part))
        except ValueError:
            continue
    return ids or None


def _parse_allowed_chat_ids(raw: str | None) -> set[int] | None:
    if not raw:
        return None
    ids: set[int] = set()
    for part in raw.replace(" ", "").split(","):
        if not part:
            continue
        try:
            ids.add(int(part))
        except ValueError:
            continue
    return ids or None


def _bool_env(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip() in ("1", "true", "True", "yes", "YES", "on", "ON")


def _allowed_user_ids() -> set[int] | None:
    return _parse_allowed_user_ids(os.getenv("TELEGRAM_ALLOWED_USER_IDS"))


def _allowed_chat_ids() -> set[int] | None:
    return _parse_allowed_chat_ids(os.getenv("TELEGRAM_ALLOWED_CHAT_IDS"))


def _require_allowlist() -> bool:
    # Safe default: if not set, allow behavior remains as before.
    # When set, bot is locked down unless allowlist is provided.
    return _bool_env("TELEGRAM_REQUIRE_ALLOWLIST", default=False)


def _allow_groups() -> bool:
    return _bool_env("TELEGRAM_ALLOW_GROUPS", default=False)


def _rate_limit_per_min() -> int:
    try:
        return int(os.getenv("TELEGRAM_RATE_LIMIT_PER_MIN", "12"))
    except Exception:
        return 12


_RATE_LIMIT_WINDOW_S = 60.0
_user_timestamps: dict[int, deque[float]] = defaultdict(lambda: deque(maxlen=200))


def _send_run_md() -> bool:
    return _bool_env("TELEGRAM_SEND_RUN_MD", default=False)


def _is_allowed(update: Update) -> bool:
    user_allow = _allowed_user_ids()
    chat_allow = _allowed_chat_ids()

    # If allowlist is required, missing allowlist means deny by default.
    if _require_allowlist() and user_allow is None and chat_allow is None:
        return False

    # If groups are not allowed, only allow private chats.
    chat = getattr(update, "effective_chat", None)
    chat_type = getattr(chat, "type", None)
    if not _allow_groups() and chat_type not in (None, "private"):
        return False

    # Enforce user allowlist if configured.
    user = getattr(update, "effective_user", None)
    if not user or user.id is None:
        return False
    if user_allow is not None and int(user.id) not in user_allow:
        return False

    # Enforce chat allowlist if configured.
    if chat_allow is not None:
        if not chat or getattr(chat, "id", None) is None:
            return False
        if int(chat.id) not in chat_allow:
            return False

    return True


def _rate_limited(update: Update) -> bool:
    user = getattr(update, "effective_user", None)
    if not user or user.id is None:
        return False
    uid = int(user.id)
    now = time.monotonic()
    dq = _user_timestamps[uid]
    dq.append(now)
    while dq and (now - dq[0]) > _RATE_LIMIT_WINDOW_S:
        dq.popleft()
    return len(dq) > _rate_limit_per_min()


async def _reject(update: Update, message: str) -> None:
    if update.message:
        await update.message.reply_text(message)


async def _guard(update: Update, *, sensitive: bool = False) -> bool:
    if not _is_allowed(update):
        await _reject(update, "접근 불가. (화이트리스트/채팅 제한)")
        return False
    if sensitive:
        # Sensitive commands should never be open by default.
        # If no allowlist is configured, deny even if general access is open.
        if _allowed_user_ids() is None and _allowed_chat_ids() is None:
            await _reject(update, "접근 불가. (민감 커맨드는 화이트리스트 설정 필요)")
            return False
    if _rate_limited(update):
        await _reject(update, "요청이 너무 많아. 잠깐만 쉬고 다시 보내줘.")
        return False
    return True


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update):
        return
    await update.message.reply_text(
        _format_for_telegram_html(
            "RAG 봇 준비됨.\n"
            "- 그냥 질문 보내면 답변함\n"
            "- /what: 이 봇이 하는 일(RAG 구조)\n"
            "- /about: 프로젝트 소개\n"
            "- /run: 실행 방법\n"
            "- /where <키워드>: 저장소에서 키워드 위치 찾기\n"
            "- /status: 브랜치/커밋/최근 결과\n"
            "- /sources: 최근 답변의 출처 보기\n"
            "- /save: 최근 답변을 outputs/에 저장 + 파일로 전송\n"
            "- /reindex: 문서 다시 인덱싱\n"
        ),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def cmd_what(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update):
        return
    await _reply_long(update, _BOT_WHAT_TEXT)


async def cmd_about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update):
        return
    about = context.application.bot_data.get("about_text") or ""
    if not about:
        about = "프로젝트 소개를 불러오지 못했어."
    await _reply_long(update, about)


async def cmd_run(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update):
        return
    text = (
        "로컬 실행 요약:\n"
        "1) `.env`에 `TELEGRAM_BOT_TOKEN`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY` 설정\n"
        "2) `pip install -r requirements.txt`\n"
        "3) `python scripts/telegram_bot.py --verbose`\n"
    )
    await update.message.reply_text(
        _format_for_telegram_html(text),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


def _run_git(args: list[str]) -> str:
    try:
        out = subprocess.check_output(["git", *args], cwd=str(_REPO_ROOT), text=True, stderr=subprocess.DEVNULL)
        return out.strip()
    except Exception:
        return ""


def _read_repo_one_liner() -> str:
    readme = _REPO_ROOT / "README.md"
    try:
        lines = readme.read_text(encoding="utf-8").splitlines()
    except Exception:
        return ""
    for line in lines[:40]:
        s = line.strip()
        if not s:
            continue
        if s.startswith("<"):  # skip HTML tags (<div>, <br/>, badges, etc.)
            continue
        s = re.sub(r"^#{1,6}\s+", "", s).strip()
        if len(s) >= 10:
            return s
    return ""


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update, sensitive=True):
        return
    branch = (
        _run_git(["rev-parse", "--abbrev-ref", "HEAD"])
        or os.getenv("RAILWAY_GIT_BRANCH")
        or "(unknown)"
    )
    sha = _run_git(["log", "-1", "--oneline"])
    if not sha:
        raw_sha = os.getenv("RAILWAY_GIT_COMMIT_SHA", "")
        sha = raw_sha[:12] if raw_sha else "(no git log)"
    head = sha

    latest_runs = []
    runs_dir = _REPO_ROOT / "outputs" / "runs"
    if runs_dir.exists():
        latest_runs = sorted(
            runs_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True
        )[:1]
    latest_run = latest_runs[0].name if latest_runs else "(none)"

    one_liner = _read_repo_one_liner()
    msg = (
        f"{('한 줄 요약: ' + one_liner + chr(10)) if one_liner else ''}"
        f"브랜치: {branch}\n"
        f"최근 커밋: {head}\n"
        f"최근 run: {latest_run}\n"
    )
    await update.message.reply_text(
        _format_for_telegram_html(msg),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def cmd_where(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update):
        return
    if not update.message:
        return
    query = update.message.text.replace("/where", "", 1).strip()
    if not query:
        await update.message.reply_text("사용법: /where <키워드>")
        return

    hits = grep_repo(_REPO_ROOT, query, limit=12)
    if not hits:
        await update.message.reply_text("못 찾았어.")
        return

    lines = ["검색 결과(상위 일부):"]
    for h in hits:
        lines.append(f"- `{h['path']}:{h['line']}` {h['snippet']}")
    await update.message.reply_text(
        _format_for_telegram_html("\n".join(lines)),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def cmd_whoami(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    user = update.effective_user
    chat = update.effective_chat

    uid = getattr(user, "id", None)
    uname = getattr(user, "username", None)
    cid = getattr(chat, "id", None)

    uname_str = f"@{uname}" if uname else "(없음)"
    text = (
        "당신의 정보는 다음과 같습니다.\n"
        "관리자에게 아래 내용을 보내주시면 접근 권한을 등록해드립니다.\n\n"
        f"- **User ID**: `{uid}`\n"
        f"- **Username**: {uname_str}\n"
        f"- **Chat ID**: `{cid}`\n"
    )
    await update.message.reply_text(
        _format_for_telegram_html(text),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def cmd_sources(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update):
        return
    last = context.chat_data.get("last_result")
    if not last:
        await update.message.reply_text("아직 질문한 적 없음.")
        return
    sources = last.get("retrieved_sources") or []
    if not sources:
        await update.message.reply_text("출처 없음.")
        return

    lines = ["최근 답변 출처:"]
    for s in sources:
        lines.append(f"- [{s.get('source')}] (score: {s.get('score')})")
    await update.message.reply_text(
        _format_for_telegram_html("\n".join(lines)),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def cmd_save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update, sensitive=True):
        return
    last = context.chat_data.get("last_result_obj")
    if not last:
        await update.message.reply_text("저장할 최근 결과가 없음. 먼저 질문해줘.")
        return

    json_path, md_path = save_result(last)
    await update.message.reply_text(
        _format_for_telegram_html(f"저장 완료:\n- `{json_path}`\n- `{md_path}`"),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    try:
        await update.message.reply_document(document=md_path.open("rb"), filename=md_path.name)
        await update.message.reply_document(document=json_path.open("rb"), filename=json_path.name)
    except Exception as e:
        logger.warning("Failed to send documents: %s", e)


async def cmd_reindex(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update, sensitive=True):
        return
    pipeline: RAGPipeline = context.application.bot_data["pipeline"]
    docs_path: str = context.application.bot_data.get("docs_path", "")
    repo_kb_cfg: RepoKBConfig = context.application.bot_data.get("repo_kb_cfg")  # type: ignore[assignment]

    await update.message.reply_text(
        _format_for_telegram_html("인덱싱 시작..."),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )
    if docs_path == "__repo__":
        docs = load_repo_documents(_REPO_ROOT, cfg=repo_kb_cfg)
        n = pipeline.index_documents(docs)
    else:
        n = pipeline.index_documents(docs_path)
    if getattr(pipeline, "_index_dir", None):
        pipeline.save_index(pipeline._index_dir)  # type: ignore[attr-defined]
    await update.message.reply_text(
        _format_for_telegram_html(f"인덱싱 완료. chunks={n}"),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update):
        return
    if not update.message or not update.message.text:
        return

    question = update.message.text.strip()
    if not question:
        return

    pipeline: RAGPipeline = context.application.bot_data["pipeline"]
    try:
        result = pipeline.query(question)
    except Exception as e:
        logger.exception("Query failed")
        await update.message.reply_text(f"에러: {e}")
        return

    def _looks_truncated(s: str) -> bool:
        s = (s or "").strip()
        if len(s) < 80:
            return False
        # If it ends with common incomplete tokens / lacks a sentence terminator, assume truncation.
        if s.endswith((":", "-", "(", "“", "「", "『", "…")):
            return True
        if s[-1] not in (".", "!", "?", ")", "]", "”", "」", "』", "…"):
            return True
        return False

    stop_reason = None
    if result.generation_output is not None:
        stop_reason = (result.generation_output.metadata or {}).get("stop_reason")
    if stop_reason == "max_tokens" or _looks_truncated(result.answer):
        # Don't regenerate the whole answer; just continue and finish the trailing sentence(s).
        cont_q = (
            "방금 답변이 문장 중간에 끊긴 것 같아. 아래 답변을 **이어서** 자연스럽게 마무리해줘.\n"
            "- 이미 말한 내용은 반복하지 마\n"
            "- 1~3문장만 추가\n"
            "- 마지막은 마침표로 끝내\n"
            "- 코드 블록/긴 인용 금지(파일 경로만 언급)\n\n"
            f"[질문]\n{question}\n\n"
            f"[현재 답변]\n{result.answer}\n\n"
            "[이어쓰기]\n"
        )
        try:
            cont = pipeline.query(cont_q)
            extra = (cont.answer or "").strip()
            if extra and extra not in result.answer:
                result.answer = (result.answer.rstrip() + "\n\n" + extra).strip()
        except Exception:
            pass

    context.chat_data["last_result"] = {
        "question": result.question,
        "answer": result.answer,
        "retrieved_sources": result.retrieved_sources,
    }
    context.chat_data["last_result_obj"] = result

    await _reply_long(update, result.answer)

    if _send_run_md():
        md = format_result_markdown(result)
        await update.message.reply_text(
            md[:3500],
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )


def build_app(*, config: str, docs: str, verbose: bool = False) -> Application:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    load_env()
    token = get_api_key("TELEGRAM_BOT_TOKEN")

    pipeline = RAGPipeline.from_config(config)
    docs_path = str(Path(docs))
    repo_kb_cfg = RepoKBConfig(
        include_dirs=("docs",),
        include_files=("README.md", "CLAUDE.md"),
        exts=(".md", ".txt", ".yaml", ".yml"),
    )

    if not getattr(pipeline, "retriever", None):
        raise RuntimeError("Pipeline init failed")

    if not isinstance(pipeline.generator, AnthropicGenerator):
        pipeline.generator = AnthropicGenerator()

    if not getattr(pipeline, "_index_dir", None):
        logger.info("No retrieval.index_dir configured; indexing on startup.")
        if docs_path == "__repo__":
            docs_obj = load_repo_documents(_REPO_ROOT, cfg=repo_kb_cfg)
            pipeline.index_documents(docs_obj)
        else:
            pipeline.index_documents(docs_path)
    else:
        if not pipeline.try_load_index(pipeline._index_dir):  # type: ignore[attr-defined]
            if docs_path == "__repo__":
                docs_obj = load_repo_documents(_REPO_ROOT, cfg=repo_kb_cfg)
                pipeline.index_documents(docs_obj)
            else:
                pipeline.index_documents(docs_path)
            pipeline.save_index(pipeline._index_dir)  # type: ignore[attr-defined]

    app = Application.builder().token(token).build()
    app.bot_data["pipeline"] = pipeline
    app.bot_data["docs_path"] = docs_path
    app.bot_data["repo_kb_cfg"] = repo_kb_cfg
    try:
        app.bot_data["about_text"] = (_REPO_ROOT / "README.md").read_text(encoding="utf-8")
    except Exception:
        app.bot_data["about_text"] = ""

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("what", cmd_what))
    app.add_handler(CommandHandler("intro", cmd_what))
    app.add_handler(CommandHandler("about", cmd_about))
    app.add_handler(CommandHandler("run", cmd_run))
    app.add_handler(CommandHandler("where", cmd_where))
    app.add_handler(CommandHandler("whoami", cmd_whoami))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("sources", cmd_sources))
    app.add_handler(CommandHandler("save", cmd_save))
    app.add_handler(CommandHandler("reindex", cmd_reindex))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))

    return app


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Telegram bot for GitHub KB RAG")
    parser.add_argument("--config", default="configs/experiments/rag_github_bot.yaml")
    parser.add_argument("--docs", default="__repo__")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    app = build_app(config=args.config, docs=args.docs, verbose=args.verbose)
    logger.info("Telegram bot running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

