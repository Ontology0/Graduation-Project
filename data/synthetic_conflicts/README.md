# Synthetic conflict pilot dataset

## Files

| File | Description |
|------|-------------|
| `pilot_conflicts.jsonl` | 10 fictional inter-context conflict cases for RAG pilot runs (English) |

**Status:** Pilot scaffolding only — not benchmark results, not real-world facts.

## Schema vs `data/schema/conflict_annotation.schema.json`

These formats serve **different stages** of the pipeline:

| Aspect | `conflict_annotation.schema.json` | `pilot_conflicts.jsonl` (this folder) |
|--------|-----------------------------------|----------------------------------------|
| Purpose | DPO / preference annotation, context–memory labeling | Multi-document **retrieval** pilot (index several docs, ask one question) |
| Evidence | Single `external_evidence` string | `documents[]` with `doc_id`, `text`, `stance` |
| Conflict label | `context-memory`, `inter-context`, … | Pilot subtype: `temporal`, `source_disagreement`, `version_update` |
| Answers | `chosen_answer` / `rejected_answer` | `gold_answer` (evaluation reference only) |
| Extra fields | `resolution_rule`, `internal_answer`, … | Omitted here; add at eval time if needed |

**Why not the same schema?** The annotation schema is `additionalProperties: false` and models one gold passage plus chosen/rejected strings. The pilot needs **multiple indexable chunks** with explicit outdated/current/distractor roles for retrieval experiments. All cases remain **fictional** and aligned with the project’s context–memory / inter-context research (retrieved docs disagree; `gold_answer` follows the `current` stance per case notes).

### Rough field mapping (for future converters)

| Pilot field | Annotation schema (approx.) |
|-------------|-----------------------------|
| `gold_answer` | `chosen_answer` |
| `documents` where `stance == "current"` | `external_evidence` (concatenate or pick top-1) |
| `documents` where `stance == "outdated"` | Contradicting context (often mimics stale parametric knowledge) |
| `conflict_type` (pilot) | Use `inter-context` in annotation export; pilot subtype stored in `notes` |

## Document stances

| Stance | Meaning |
|--------|---------|
| `current` | Authoritative answer for the question (matches `gold_answer`) |
| `outdated` | Superseded or incorrect for the question as asked |
| `distractor` | Plausible but irrelevant or off-topic for the question |

## Batch run

```bash
# Base RAG (all 10 pilot cases)
python scripts/run_batch.py \
  --config configs/experiments/rag_base.yaml \
  --dataset data/synthetic_conflicts/pilot_conflicts.jsonl

# Conflict-aware prompting
python scripts/run_batch.py \
  --config configs/experiments/prompting_conflict_aware.yaml \
  --dataset data/synthetic_conflicts/pilot_conflicts.jsonl

# Debug: first 2 cases only
python scripts/run_batch.py \
  --config configs/experiments/rag_base.yaml \
  --dataset data/synthetic_conflicts/pilot_conflicts.jsonl \
  --limit 2
```

Results: `outputs/{experiment_name}/pilot_conflicts_{UTC_timestamp}.jsonl`  
Each line includes `case_id`, `question`, `gold_answer`, `predicted_answer`, `retrieved_sources`, `config_name`, `conflict_type`.
