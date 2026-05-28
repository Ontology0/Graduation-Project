#!/usr/bin/env python3
"""CLI script to run the RAG pipeline from a config file."""

import argparse
import logging

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.rag.pipeline import RAGPipeline
from src.rag.reporting import save_result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the RAG pipeline")
    parser.add_argument(
        "--config",
        default="configs/experiments/rag_base.yaml",
        help="Path to experiment YAML config",
    )
    parser.add_argument("--docs", required=True, help="Path to documents to index")
    parser.add_argument("--question", required=True, help="Question to ask")
    parser.add_argument("--top-k", type=int, default=None, help="Override top-k retrieval count")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--out-dir",
        default="outputs/runs",
        help="Directory to write JSON/MD results",
    )
    parser.add_argument(
        "--run-name",
        default=None,
        help="Optional output filename stem (default: UTC timestamp)",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    pipeline = RAGPipeline.from_config(args.config)
    pipeline.index_documents(args.docs)
    if getattr(pipeline, "_index_dir", None):
        pipeline.save_index(pipeline._index_dir)  # type: ignore[attr-defined]
    result = pipeline.query(args.question, top_k=args.top_k)

    print(f"\nQuestion: {result.question}")
    print(f"\nAnswer: {result.answer}")
    print(f"\nSources:")
    for s in result.retrieved_sources:
        print(f"  - [{s['source']}] (score: {s['score']})")

    json_path, md_path = save_result(result, out_dir=args.out_dir, run_name=args.run_name)
    print(f"\nSaved run:")
    print(f"  - JSON: {json_path}")
    print(f"  - MD:   {md_path}")


if __name__ == "__main__":
    main()
