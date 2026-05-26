#!/usr/bin/env python3
"""Run RAG over a JSONL conflict pilot dataset and write results to outputs/."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.rag.config import load_config, resolve_path
from src.rag.pilot_dataset import (
    batch_output_path,
    documents_from_case,
    load_conflict_dataset,
)
from src.rag.pipeline import RAGPipeline, RAGResult

logger = logging.getLogger(__name__)


def batch_record(case: dict[str, Any], result: RAGResult) -> dict[str, Any]:
    """Merge dataset fields with :class:`RAGResult` for one output line."""
    record = {
        "case_id": case.get("id", ""),
        "question": case.get("question", result.question),
        "gold_answer": case.get("gold_answer", ""),
        "conflict_type": case.get("conflict_type", ""),
    }
    record.update(result.to_dict(include_generation=True))
    return record


def write_jsonl(records: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def run_batch(
    pipeline: RAGPipeline,
    cases: list[dict[str, Any]],
    *,
    use_tqdm: bool = True,
) -> list[dict[str, Any]]:
    """Index and query each case with a fresh vector store."""
    records: list[dict[str, Any]] = []
    total = len(cases)

    tqdm_bar = None
    if use_tqdm:
        try:
            from tqdm import tqdm

            tqdm_bar = tqdm
        except ImportError:
            tqdm_bar = None

    case_iter = tqdm_bar(cases, desc="cases", total=total) if tqdm_bar else cases

    for i, case in enumerate(case_iter, 1):
        case_id = case.get("id", f"case_{i}")
        if tqdm_bar is None:
            print(f"[{i}/{total}] {case_id} ...", flush=True)

        pipeline.reset_index()
        pipeline.index_documents(documents_from_case(case))
        result = pipeline.query(str(case["question"]))
        records.append(batch_record(case, result))
        logger.info("Finished case %s", case_id)

    return records


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Batch RAG runs over a synthetic conflict JSONL dataset",
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Experiment YAML config (e.g. configs/experiments/rag_base.yaml)",
    )
    parser.add_argument(
        "--dataset",
        required=True,
        help="JSONL dataset path (e.g. data/synthetic_conflicts/pilot_conflicts.jsonl)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Run only the first N cases (debugging)",
    )
    parser.add_argument(
        "--output_dir",
        default="outputs",
        help="Root directory for run artifacts (default: outputs/)",
    )
    parser.add_argument(
        "--no-tqdm",
        action="store_true",
        help="Use print progress instead of tqdm",
    )
    parser.add_argument("--verbose", action="store_true", help="Debug logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    config_path = resolve_path(args.config)
    dataset_path = resolve_path(args.dataset)
    output_root = resolve_path(args.output_dir)

    cfg = load_config(config_path)
    experiment_name = str(cfg.get("experiment_name") or config_path.stem)

    cases = load_conflict_dataset(dataset_path, limit=args.limit)
    logger.info("Loaded %d case(s) from %s", len(cases), dataset_path)

    pipeline = RAGPipeline.from_config(config_path)
    records = run_batch(pipeline, cases, use_tqdm=not args.no_tqdm)

    out_file = batch_output_path(output_root, experiment_name, dataset_path)
    write_jsonl(records, out_file)

    print(f"\nWrote {len(records)} result(s) to {out_file}")
    print(f"Experiment: {experiment_name}")


if __name__ == "__main__":
    main()
