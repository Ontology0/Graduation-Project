#!/usr/bin/env python3
"""CLI script to run the RAG pipeline from a config file."""

import argparse
import logging

from src.rag.pipeline import RAGPipeline


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
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    pipeline = RAGPipeline.from_config(args.config)
    pipeline.index_documents(args.docs)
    result = pipeline.query(args.question, top_k=args.top_k)

    print(f"\nExperiment: {result.config_name}")
    print(f"\nQuestion: {result.question}")
    print(f"\nAnswer: {result.answer}")
    print(f"\nSources:")
    for s in result.retrieved_sources:
        print(f"  - [{s['source']}] (score: {s['score']})")


if __name__ == "__main__":
    main()
