"""Five-arm conflict eval harness (issue #56)."""

from __future__ import annotations

import argparse
import json
import logging
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING, Any

from src.rag.config import load_config, resolve_path
from src.rag.pilot_dataset import load_conflict_dataset

if TYPE_CHECKING:
    from src.rag.pipeline import RAGPipeline

logger = logging.getLogger(__name__)

DEFAULT_EVAL_PATH = "data/synthetic_conflicts/preference_pairs_eval.jsonl"
PILOT_DATASET_PATH = "data/synthetic_conflicts/pilot_conflicts.jsonl"

RAG_INFERENCE_ARMS: frozenset[str] = frozenset(
    {"rag_base", "prompting_conflict_aware"}
)

ARM_CONFIGS: dict[str, str] = {
    "rag_base": "configs/experiments/rag_base.yaml",
    "prompting_conflict_aware": "configs/experiments/prompting_conflict_aware.yaml",
    "lora_parrag_style": "configs/experiments/lora_parrag_style.yaml",
    "lora_conflict_only": "configs/experiments/lora_conflict_only.yaml",
    "lora_conflict_parrag": "configs/experiments/lora_conflict_parrag.yaml",
}


@dataclass
class EvalCase:
    """One eval instance with fields needed for scoring."""

    id: str
    prompt: str
    gold_answer: str
    false_answer: str = ""
    case_type: str = "unknown"
    metadata: dict[str, Any] = field(default_factory=dict)


def normalize_text(text: str) -> str:
    """Normalize text for substring matching (exp2 clasheval_v2 style)."""
    lowered = text.lower()
    for token in ("approximately", "about", ","):
        lowered = lowered.replace(token, "")
    return " ".join(lowered.split())


def contains_target(answer: str, target: str) -> bool:
    """True if ``target`` appears in ``answer`` (token fallback for short gold spans)."""
    if not target or not target.strip():
        return False
    answer_norm = normalize_text(answer)
    target_norm = normalize_text(target)
    if target_norm in answer_norm:
        return True
    tokens = [tok for tok in target_norm.split() if len(tok) > 2]
    return bool(tokens) and all(tok in answer_norm for tok in tokens)


def conflict_resolution_accuracy(rows: list[dict[str, Any]]) -> float:
    """Fraction of answers containing the authoritative gold substring."""
    if not rows:
        return 0.0
    hits = sum(1 for row in rows if row.get("true_hit"))
    return hits / len(rows)


ABSTENTION_PHRASES: tuple[str, ...] = (
    "i don't know",
    "i do not know",
    "cannot determine",
    "can't determine",
    "insufficient information",
    "not enough information",
    "uncertain",
    "unable to determine",
    "모르겠",
    "불확실",
    "확실하지 않",
)


def detects_abstention(answer: str) -> bool:
    normalized = normalize_text(answer)
    return any(phrase in normalized for phrase in ABSTENTION_PHRASES)


def false_doc_follow_rate(rows: list[dict[str, Any]]) -> float:
    """Share of answers that follow false evidence without gold (vulnerability)."""
    eligible = [row for row in rows if row.get("false_answer")]
    if not eligible:
        return 0.0
    follows = sum(1 for row in eligible if row.get("false_follow_only"))
    return follows / len(eligible)


def abstention_rate(rows: list[dict[str, Any]]) -> float:
    """Share of answers expressing uncertainty / refusal to answer."""
    if not rows:
        return 0.0
    return sum(1 for row in rows if row.get("abstention")) / len(rows)


def metrics_for_rows(rows: list[dict[str, Any]]) -> dict[str, float]:
    return {
        "conflict_resolution_accuracy": conflict_resolution_accuracy(rows),
        "false_doc_follow_rate": false_doc_follow_rate(rows),
        "abstention_rate": abstention_rate(rows),
        "count": float(len(rows)),
    }


def aggregate_by_case_type(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    """Per case_type metric breakdown for capability mapping."""
    buckets: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        case_type = row.get("case_type") or "unknown"
        buckets.setdefault(case_type, []).append(row)
    return {case_type: metrics_for_rows(bucket_rows) for case_type, bucket_rows in sorted(buckets.items())}


def build_capability_map(by_case_type: dict[str, dict[str, float]]) -> dict[str, str]:
    """Summarize which conflict types meet a resolution-accuracy threshold."""
    capability: dict[str, str] = {}
    threshold = 0.5
    for case_type, metrics in by_case_type.items():
        accuracy = metrics.get("conflict_resolution_accuracy", 0.0)
        if metrics.get("count", 0) == 0:
            capability[case_type] = "no_cases"
        elif accuracy > threshold:
            capability[case_type] = "handled"
        elif accuracy > 0:
            capability[case_type] = "partial"
        else:
            capability[case_type] = "not_handled"
    return capability


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _answer_line(text: str) -> str:
    if text.startswith("Answer: "):
        return text.split("\n", 1)[0][len("Answer: ") :].strip()
    return ""


def _case_type_from_metadata(meta: dict[str, Any]) -> str:
    subtype = meta.get("original_subtype", "")
    if subtype.startswith("case_type_"):
        return subtype.split("_")[2].split("/")[0]
    if subtype in ("version_update", "temporal", "source_disagreement"):
        return f"pilot_{subtype}"
    return subtype or "unknown"


def pair_to_eval_case(pair: dict[str, Any]) -> EvalCase:
    meta = dict(pair.get("metadata") or {})
    return EvalCase(
        id=pair["id"],
        prompt=pair["prompt"],
        gold_answer=_answer_line(pair.get("chosen", "")),
        false_answer=_answer_line(pair.get("rejected", "")),
        case_type=_case_type_from_metadata(meta),
        metadata=meta,
    )


def load_eval_cases(path: str | Path) -> list[EvalCase]:
    resolved = resolve_path(path)
    if not resolved.exists():
        raise FileNotFoundError(f"Eval dataset not found: {resolved}")
    return [pair_to_eval_case(row) for row in read_jsonl(resolved)]


def resolve_arm_config(arm: str, config_override: str | None) -> dict[str, Any]:
    if arm not in ARM_CONFIGS:
        raise ValueError(f"Unknown arm {arm!r}; choose from {sorted(ARM_CONFIGS)}")
    path = config_override or ARM_CONFIGS[arm]
    return load_config(path)


def adapter_dir_for(arm: str, yaml_cfg: dict[str, Any]) -> Path | None:
    """Return checkpoint dir with LoRA adapter weights if present."""
    experiment_name = yaml_cfg.get("experiment_name", arm)
    for name in (arm, experiment_name):
        base = resolve_path("outputs/checkpoints") / name
        if (base / "adapter_config.json").exists() or any(
            base.glob("adapter_model*.safetensors")
        ):
            return base
    return None


def annotate_scoring_fields(row: dict[str, Any]) -> dict[str, Any]:
    """Add scoring flags (true/false hit, abstention) for metric aggregation."""
    predicted = row["predicted_answer"]
    gold = row["gold_answer"]
    false = row.get("false_answer", "")
    true_hit = contains_target(predicted, gold)
    false_hit = contains_target(predicted, false)
    annotated = dict(row)
    annotated["true_hit"] = true_hit
    annotated["false_hit"] = false_hit
    annotated["correct"] = true_hit
    annotated["false_follow_only"] = false_hit and not true_hit
    annotated["abstention"] = detects_abstention(predicted)
    return annotated


def load_pilot_case_index(path: str | Path = PILOT_DATASET_PATH) -> dict[str, dict[str, Any]]:
    """Map pilot case id → raw conflict record (documents + question)."""
    return {case["id"]: case for case in load_conflict_dataset(path)}


def pilot_case_for(eval_case: EvalCase, pilot_index: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    """Resolve the pilot JSONL row backing a preference-pair eval case."""
    case_id = eval_case.metadata.get("source_record_id") or eval_case.id
    return pilot_index.get(str(case_id))


def predict_rag(
    arm: str,
    case: EvalCase,
    pipeline: RAGPipeline,
    pilot_index: dict[str, dict[str, Any]],
) -> str:
    """Run Base RAG or Conflict-Aware Prompting via :class:`RAGPipeline`."""
    from src.rag.pilot_dataset import documents_from_case

    pilot = pilot_case_for(case, pilot_index)
    if pilot is None:
        raise ValueError(f"No pilot case found for eval id {case.id!r}")

    pipeline.reset_index()
    pipeline.index_documents(documents_from_case(pilot))
    return pipeline.query(str(pilot["question"])).answer


def predict_placeholder(arm: str, case: EvalCase, yaml_cfg: dict[str, Any]) -> str:
    """Arm-specific generation placeholder until full RAG/LoRA inference is wired."""
    adapter = adapter_dir_for(arm, yaml_cfg)
    model_name = yaml_cfg.get("model_name", "unknown")
    adapter_note = f"adapter={adapter}" if adapter else "adapter=none(base)"
    return (
        f"[eval-placeholder arm={arm} model={model_name} {adapter_note}] "
        f"case_id={case.id}"
    )


def run_arm(
    arm: str,
    cases: list[EvalCase],
    *,
    config_override: str | None = None,
    output_dir: Path,
) -> list[dict[str, Any]]:
    config_path = config_override or ARM_CONFIGS[arm]
    yaml_cfg = resolve_arm_config(arm, config_override)
    output_dir.mkdir(parents=True, exist_ok=True)
    results_path = output_dir / "results.jsonl"

    pipeline: RAGPipeline | None = None
    pilot_index: dict[str, dict[str, Any]] | None = None
    if arm in RAG_INFERENCE_ARMS:
        from src.rag.pipeline import RAGPipeline

        pipeline = RAGPipeline.from_config(config_path)
        pilot_index = load_pilot_case_index()

    rows: list[dict[str, Any]] = []
    with results_path.open("w", encoding="utf-8") as handle:
        for case in cases:
            if arm in RAG_INFERENCE_ARMS and pipeline is not None and pilot_index is not None:
                try:
                    predicted = predict_rag(arm, case, pipeline, pilot_index)
                except Exception as exc:
                    logger.warning(
                        "RAG inference failed for arm=%s case=%s: %s",
                        arm,
                        case.id,
                        exc,
                    )
                    predicted = predict_placeholder(arm, case, yaml_cfg)
            else:
                predicted = predict_placeholder(arm, case, yaml_cfg)
            row = {
                "id": case.id,
                "arm": arm,
                "prompt": case.prompt,
                "predicted_answer": predicted,
                "gold_answer": case.gold_answer,
                "false_answer": case.false_answer,
                "case_type": case.case_type,
                "metadata": case.metadata,
            }
            scored = annotate_scoring_fields(row)
            rows.append(scored)
            handle.write(json.dumps(scored, ensure_ascii=False) + "\n")

    by_case_type = aggregate_by_case_type(rows)
    summary = {
        "arm": arm,
        "experiment_name": yaml_cfg.get("experiment_name"),
        "model_name": yaml_cfg.get("model_name"),
        "adapter_dir": str(adapter_dir_for(arm, yaml_cfg) or ""),
        "inference_mode": "rag_pipeline" if arm in RAG_INFERENCE_ARMS else "placeholder",
        "num_cases": len(rows),
        "metrics": metrics_for_rows(rows),
        "by_case_type": by_case_type,
        "capability_map": build_capability_map(by_case_type),
    }
    summary_path = output_dir / "summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    logger.info("Wrote %s and %s", results_path, summary_path)
    return rows


def default_output_root(output_dir: str | None) -> Path:
    if output_dir:
        return resolve_path(output_dir)
    stamp = date.today().strftime("%Y%m%d")
    return resolve_path("experiments") / stamp


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Five-arm conflict evaluation runner")
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Override experiment YAML for a single --arm run",
    )
    parser.add_argument(
        "--arm",
        type=str,
        default=None,
        choices=sorted(ARM_CONFIGS),
        help="Run one arm (default: all five)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Base output directory (default: experiments/YYYYMMDD/eval_{arm}/)",
    )
    parser.add_argument(
        "--eval-data",
        type=str,
        default=DEFAULT_EVAL_PATH,
        help="Eval preference-pair JSONL path",
    )
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    cases = load_eval_cases(args.eval_data)
    arms = [args.arm] if args.arm else sorted(ARM_CONFIGS)
    root = default_output_root(args.output_dir)

    for arm in arms:
        arm_dir = root / f"eval_{arm}"
        run_arm(arm, cases, config_override=args.config, output_dir=arm_dir)


if __name__ == "__main__":
    main()
