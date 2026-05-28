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

import sys

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from src.rag.config import get_api_key, load_env
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
        "- /sources: 최근 답변의 출처 보기\n"
        "- /save: 최근 답변을 outputs/에 저장 + 파일로 전송\n"
        "- /reindex: 문서 다시 인덱싱\n"
    )


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
    docs_path: str = context.application.bot_data["docs_path"]

    await update.message.reply_text("인덱싱 시작...")
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
    parser.add_argument("--config", default="configs/experiments/rag_base.yaml")
    parser.add_argument("--docs", required=True, help="Path to documents to index")
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

    if not getattr(pipeline, "_index_dir", None):
        logger.info("No retrieval.index_dir configured; indexing on startup.")
        pipeline.index_documents(docs_path)
    else:
        if not pipeline.try_load_index(pipeline._index_dir):  # type: ignore[attr-defined]
            pipeline.index_documents(docs_path)
            pipeline.save_index(pipeline._index_dir)  # type: ignore[attr-defined]

    app = Application.builder().token(token).build()
    app.bot_data["pipeline"] = pipeline
    app.bot_data["docs_path"] = docs_path

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("sources", cmd_sources))
    app.add_handler(CommandHandler("save", cmd_save))
    app.add_handler(CommandHandler("reindex", cmd_reindex))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))

    logger.info("Telegram bot running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

