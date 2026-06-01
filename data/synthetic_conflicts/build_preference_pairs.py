"""Build DPO preference pairs from conflict JSONL sources (scaffold)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from src.rag.document_loader import Document
from src.rag.prompt_builder import PromptTemplate, build_prompt, load_prompt_template
from src.rag.retriever import RetrievalResult

CONFLICT_AWARE_PROMPT = "configs/prompts/conflict_aware.md"
_PROMPT_TEMPLATE: PromptTemplate | None = None

# Pilot (current/outdated/distractor) and exp2 (true_doc/false_doc/distractor).
STANCE_TO_ROLE: dict[str, str] = {
    "current": "authoritative",
    "true_doc": "authoritative",
    "outdated": "contradicting",
    "false_doc": "contradicting",
    "distractor": "distractor",
}


def map_stance_to_role(stance: str) -> str:
    """Map source stance label to normalized document role."""
    try:
        return STANCE_TO_ROLE[stance]
    except KeyError as exc:
        raise ValueError(f"Unknown stance: {stance!r}") from exc


def annotate_document_roles(documents: list[dict]) -> list[dict]:
    """Return documents with an added ``role`` field from ``stance``."""
    annotated: list[dict] = []
    for doc in documents:
        doc_copy = dict(doc)
        doc_copy["role"] = map_stance_to_role(doc["stance"])
        annotated.append(doc_copy)
    return annotated


def is_pilot_record(record: dict) -> bool:
    return "conflict_type" in record and "case_type" not in record


def is_exp2_record(record: dict) -> bool:
    return "case_type" in record


def is_train_eligible(record: dict) -> bool:
    """Train split: unambiguous cases per docs/decision_log.md (#55)."""
    if is_pilot_record(record):
        return record["conflict_type"] in ("version_update", "temporal")
    if is_exp2_record(record):
        return record.get("case_type") == "B" or record.get("has_true_doc") is True
    return False


def filter_records_for_split(records: list[dict], split: str) -> list[dict]:
    if split == "train":
        return [r for r in records if is_train_eligible(r)]
    if split == "eval":
        return list(records)
    raise ValueError(f"Unknown split: {split!r}")


def read_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def load_all_inputs(input_paths: list[Path]) -> list[dict]:
    merged: list[dict] = []
    for path in input_paths:
        merged.extend(read_jsonl(path))
    return merged


def get_prompt_template() -> PromptTemplate:
    global _PROMPT_TEMPLATE
    if _PROMPT_TEMPLATE is None:
        _PROMPT_TEMPLATE = load_prompt_template(CONFLICT_AWARE_PROMPT)
    return _PROMPT_TEMPLATE


def documents_to_results(documents: list[dict]) -> list[RetrievalResult]:
    results: list[RetrievalResult] = []
    for index, doc in enumerate(documents, 1):
        doc_id = doc.get("doc_id", f"d{index}")
        stance = doc.get("stance", "")
        source = f"{doc_id}:{stance}" if stance else doc_id
        results.append(
            RetrievalResult(
                document=Document(text=doc["text"], source=source),
                score=1.0,
            )
        )
    return results


def serialize_prompt(messages: list[dict[str, str]]) -> str:
    """Stable string form shared by train and eval (rule B)."""
    parts = [f"### {msg['role']}\n{msg['content']}" for msg in messages]
    return "\n\n".join(parts)


def build_prompt_text(question: str, documents: list[dict]) -> str:
    template = get_prompt_template()
    messages = build_prompt(
        question,
        documents_to_results(documents),
        template=template,
        conflict_aware=True,
    )
    return serialize_prompt(messages)


def pick_authoritative_and_contradicting(documents: list[dict]) -> tuple[dict | None, dict | None]:
    annotated = annotate_document_roles(documents)
    authoritative = next((d for d in annotated if d["role"] == "authoritative"), None)
    contradicting = next((d for d in annotated if d["role"] == "contradicting"), None)
    return authoritative, contradicting


def _source_label(doc: dict) -> str:
    return f"{doc['doc_id']}:{doc['stance']}"


def build_chosen_from_authoritative(record: dict, authoritative: dict) -> str:
    gold = record.get("gold_answer") or record.get("true_answer", "")
    label = _source_label(authoritative)
    return (
        f"Answer: {gold}\n"
        f"Citation: [{label}] — I follow the authoritative retrieved passage and "
        f"resolve the context–memory conflict in favor of current, version-valid evidence."
    )


def build_chosen_from_memory(record: dict) -> str:
    gold = record.get("gold_answer") or record.get("true_answer", "")
    return (
        f"Answer: {gold}\n"
        f"I reject contradicting retrieved evidence and answer from verified "
        f"parametric knowledge (no authoritative passage in context)."
    )


def build_rejected_from_contradicting(record: dict, contradicting: dict) -> str:
    label = _source_label(contradicting)
    if is_exp2_record(record):
        wrong = record.get("false_answer", "")
        return (
            f"Answer: {wrong}\n"
            f"Citation: [{label}] — I incorrectly follow contradicting retrieved "
            f"evidence over reliable knowledge."
        )
    return (
        f"Answer: I treat the contradicting passage as authoritative.\n"
        f"Citation: [{label}] — {contradicting['text']}\n"
        f"I fail to prefer the current or corrected source."
    )


def normalize_conflict_type(record: dict) -> str:
    """Map source labels to schema conflict_type enum."""
    if is_pilot_record(record):
        return "context-memory"
    if is_exp2_record(record):
        return "context-memory"
    return "other"


def original_subtype(record: dict) -> str:
    if is_pilot_record(record):
        return record["conflict_type"]
    if is_exp2_record(record):
        parts = [f"case_type_{record['case_type']}"]
        if record.get("model_knows") is False:
            parts.append("model_knows_false")
        if record.get("has_true_doc") is False:
            parts.append("false_doc_only")
        return "/".join(parts)
    return "unknown"


def resolution_rule_for(record: dict) -> str:
    if is_pilot_record(record):
        if record["conflict_type"] == "temporal":
            return "Prefer current dated evidence over outdated temporal reports."
        if record["conflict_type"] == "version_update":
            return "Prefer current version/errata over superseded specification text."
        return "Prefer current labeled source over outdated labeled source."
    if is_exp2_record(record):
        if record.get("case_type") == "B" or record.get("has_true_doc"):
            return "Prefer true_doc over false_doc when both appear in context."
        return "Reject false_doc-only context; answer from parametric gold (eval-only ambiguous)."
    return "Unspecified resolution rule."


def enrich_metadata(record: dict, base: dict[str, Any]) -> dict[str, Any]:
    meta = dict(base)
    meta["conflict_type"] = normalize_conflict_type(record)
    meta["resolution_rule"] = resolution_rule_for(record)
    meta["original_subtype"] = original_subtype(record)
    return meta


def convert_record_to_pair(record: dict) -> dict[str, Any] | None:
    authoritative, contradicting = pick_authoritative_and_contradicting(record["documents"])
    if contradicting is None:
        return None

    prompt = build_prompt_text(record["question"], record["documents"])
    if authoritative is not None:
        chosen = build_chosen_from_authoritative(record, authoritative)
    else:
        chosen = build_chosen_from_memory(record)
    rejected = build_rejected_from_contradicting(record, contradicting)

    return {
        "id": record["id"],
        "prompt": prompt,
        "chosen": chosen,
        "rejected": rejected,
        "metadata": enrich_metadata(record, {"source_record_id": record["id"]}),
    }


def convert_records(records: list[dict]) -> list[dict[str, Any]]:
    pairs: list[dict[str, Any]] = []
    for record in records:
        pair = convert_record_to_pair(record)
        if pair is not None:
            pairs.append(pair)
    return pairs


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert conflict JSONL to preference pairs.")
    parser.add_argument(
        "--input",
        action="append",
        required=True,
        help="Input conflict JSONL path (repeatable).",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory for preference_pairs_{split}.jsonl output.",
    )
    parser.add_argument(
        "--split",
        choices=("train", "eval"),
        required=True,
        help="Split name for output file and filtering (logic added in later commits).",
    )
    args = parser.parse_args()

    records = load_all_inputs([Path(p) for p in args.input])
    records = filter_records_for_split(records, args.split)

    pairs = convert_records(records)
    output_path = Path(args.output_dir) / f"preference_pairs_{args.split}.jsonl"
    write_jsonl(output_path, pairs)


if __name__ == "__main__":
    main()
