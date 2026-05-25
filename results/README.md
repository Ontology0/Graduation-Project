# results/

## Purpose

Stores experiment outputs: logs, tables, figures, and exported reports produced by `eval/`, `rag/`, or `finetuning/` runs.

## Current status

**No final experimental results are reported yet.**

Do not add placeholder accuracy, fake RAGAS numbers, or synthetic benchmark leaderboards.

## Experiment result folder template

When a run is executed, create one folder per experiment, for example:

```text
results/YYYY-MM-DD_<experiment_name>/
├── config.yaml          # Copy or snapshot of configs/*.yaml used
├── metrics.json         # Aggregated metrics (empty or omitted until computed)
├── predictions.jsonl    # One JSON object per example (id, prompt, prediction, ...)
├── error_analysis.md    # Qualitative failure notes
└── README.md            # Short run description, git commit hash, data split
```

## Per-run artifacts

| File | Description |
|------|-------------|
| `config.yaml` | Frozen hyperparameters and paths for reproduction |
| `metrics.json` | Structured metric dict — populate only from real eval runs |
| `predictions.jsonl` | Model outputs for downstream judge or human review |
| `error_analysis.md` | Conflict mis-resolution patterns, abstention failures, etc. |
| `README.md` | Human-readable summary of what was run and what is still TBD |

## Notes

- Large checkpoints and raw predictions may stay local; follow root `.gitignore`.
- Link experiment names to `configs/` and `docs/experiment_design.md` comparison arms.
