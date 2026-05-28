#!/usr/bin/env python3
"""Telegram chatbot entrypoint for the RAG pipeline.

Usage:
  python scripts/telegram_bot.py --config configs/experiments/rag_base.yaml --docs data/sample_docs/

Env:
  TELEGRAM_BOT_TOKEN=...
  (optional) ANTHROPIC_API_KEY=... when llm.provider is anthropic
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
import subprocess

import sys

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from src.rag.config import get_api_key, load_env
from src.rag.generator import AnthropicGenerator
from src.rag.github_kb import grep_repo, load_repo_documents
from src.rag.pipeline import RAGPipeline
from src.rag.reporting import format_result_markdown, save_result

logger = logging.getLogger(__name__)


def _truncate(text: str, limit: int = 3500) -> str:
    text = (text or "").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 30].rstrip() + "\n\n...(truncated)"


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "RAG 봇 준비됨.\n"
        "- 그냥 질문 보내면 답변함\n"
        "- /about: 프로젝트 소개\n"
        "- /run: 실행 방법\n"
        "- /where <키워드>: 저장소에서 키워드 위치 찾기\n"
        "- /status: 브랜치/커밋/최근 결과\n"
        "- /sources: 최근 답변의 출처 보기\n"
        "- /save: 최근 답변을 outputs/에 저장 + 파일로 전송\n"
        "- /reindex: 문서 다시 인덱싱\n"
    )

async def cmd_about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    about = context.application.bot_data.get("about_text") or ""
    if not about:
        about = "프로젝트 소개를 불러오지 못했어."
    await update.message.reply_text(_truncate(about, 3500))


async def cmd_run(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "로컬 실행 요약:\n"
        "1) `.env`에 `TELEGRAM_BOT_TOKEN`, `ANTHROPIC_API_KEY` 설정\n"
        "2) `pip install -r requirements.txt`\n"
        "3) `python scripts/telegram_bot.py --config configs/experiments/rag_github_bot.yaml --verbose`\n"
    )
    await update.message.reply_text(text)


def _run_git(args: list[str]) -> str:
    try:
        out = subprocess.check_output(["git", *args], cwd=str(_REPO_ROOT), text=True)
        return out.strip()
    except Exception:
        return ""


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    branch = _run_git(["rev-parse", "--abbrev-ref", "HEAD"]) or "(unknown)"
    head = _run_git(["log", "-1", "--oneline"]) or "(no git log)"

    latest_runs = []
    runs_dir = _REPO_ROOT / "outputs" / "runs"
    if runs_dir.exists():
        latest_runs = sorted(runs_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:1]
    latest_run = latest_runs[0].name if latest_runs else "(none)"

    msg = (
        f"브랜치: {branch}\n"
        f"최근 커밋: {head}\n"
        f"최근 run: {latest_run}\n"
    )
    await update.message.reply_text(msg)


async def cmd_where(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN)


async def cmd_sources(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
    await update.message.reply_text("\n".join(lines))


async def cmd_save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    last = context.chat_data.get("last_result_obj")
    if not last:
        await update.message.reply_text("저장할 최근 결과가 없음. 먼저 질문해줘.")
        return

    json_path, md_path = save_result(last)
    await update.message.reply_text(f"저장 완료:\n- {json_path}\n- {md_path}")

    try:
        await update.message.reply_document(document=md_path.open("rb"), filename=md_path.name)
        await update.message.reply_document(document=json_path.open("rb"), filename=json_path.name)
    except Exception as e:
        logger.warning("Failed to send documents: %s", e)


async def cmd_reindex(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pipeline: RAGPipeline = context.application.bot_data["pipeline"]
    docs_path: str = context.application.bot_data.get("docs_path", "")

    await update.message.reply_text("인덱싱 시작...")
    if docs_path == "__repo__":
        docs = load_repo_documents(_REPO_ROOT)
        n = pipeline.index_documents(docs)
    else:
        n = pipeline.index_documents(docs_path)
    if getattr(pipeline, "_index_dir", None):
        pipeline.save_index(pipeline._index_dir)  # type: ignore[attr-defined]
    await update.message.reply_text(f"인덱싱 완료. chunks={n}")


async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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

    # keep last result (dict + object)
    context.chat_data["last_result"] = {
        "question": result.question,
        "answer": result.answer,
        "retrieved_sources": result.retrieved_sources,
    }
    context.chat_data["last_result_obj"] = result

    answer = _truncate(result.answer)
    await update.message.reply_text(answer)

    # Also send a compact markdown summary (useful for provenance)
    md = format_result_markdown(result)
    await update.message.reply_text(
        _truncate(md, 3500),
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Telegram bot for RAG pipeline")
    parser.add_argument("--config", default="configs/experiments/rag_github_bot.yaml")
    parser.add_argument(
        "--docs",
        default="__repo__",
        help="Path to documents to index (default: repo knowledge base)",
    )
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    load_env()
    token = get_api_key("TELEGRAM_BOT_TOKEN")

    pipeline = RAGPipeline.from_config(args.config)
    docs_path = str(Path(args.docs))

    # Build/load index at boot
    if not getattr(pipeline, "retriever", None):
        raise RuntimeError("Pipeline init failed")

    # Force Claude for this bot.
    if not isinstance(pipeline.generator, AnthropicGenerator):
        logger.info("Forcing AnthropicGenerator for Telegram bot.")
        pipeline.generator = AnthropicGenerator()

    if not getattr(pipeline, "_index_dir", None):
        logger.info("No retrieval.index_dir configured; indexing on startup.")
        if docs_path == "__repo__":
            docs = load_repo_documents(_REPO_ROOT)
            pipeline.index_documents(docs)
        else:
            pipeline.index_documents(docs_path)
    else:
        if not pipeline.try_load_index(pipeline._index_dir):  # type: ignore[attr-defined]
            if docs_path == "__repo__":
                docs = load_repo_documents(_REPO_ROOT)
                pipeline.index_documents(docs)
            else:
                pipeline.index_documents(docs_path)
            pipeline.save_index(pipeline._index_dir)  # type: ignore[attr-defined]

    app = Application.builder().token(token).build()
    app.bot_data["pipeline"] = pipeline
    app.bot_data["docs_path"] = docs_path
    try:
        app.bot_data["about_text"] = (_REPO_ROOT / "README.md").read_text(encoding="utf-8")
    except Exception:
        app.bot_data["about_text"] = ""

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("about", cmd_about))
    app.add_handler(CommandHandler("run", cmd_run))
    app.add_handler(CommandHandler("where", cmd_where))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("sources", cmd_sources))
    app.add_handler(CommandHandler("save", cmd_save))
    app.add_handler(CommandHandler("reindex", cmd_reindex))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))

    logger.info("Telegram bot running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

