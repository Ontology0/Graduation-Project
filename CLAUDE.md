# Alltology contributor context

## Current research

The current focus is selective intervention for LLM knowledge–context conflicts: read internal signals, choose whether and how to intervene (Routing), and modify activations with the backbone weights fixed (Steering).

- Router and Packed are separate implementations; their combination is a research question, not a completed result.
- Distinguish state classification from actual answer improvement, and report accuracy, correct-context damage, and inference cost separately.
- The separate knowledge–context 4-state paper is submitted to KSC 2026 and under review. Keep its code and detailed results private.

## Where to work

| Area | Location |
|---|---|
| Experiment notebooks and public results | [experiments/](experiments/README.md) |
| Comparison code and implementation status | [SOTA/](SOTA/README.md) |
| Shared prompt and scoring helpers | [prompt/p8s_prompt.py](prompt/p8s_prompt.py) |
| Current research and activity records | [docs/](docs/README.md) |
| Initial RAG, DPO/LoRA, app, bot, and course material | [legacy/](legacy/README.md) |

Start with [README](README.md), [getting started](docs/getting_started.md), and [research results](docs/research_status.md). Use [team contributions](docs/team_contributions.md) for actual research, writing, and presentation roles; upload authorship alone does not establish research authorship.

## Working rules

- Keep current experiments independent of the archived RAG package in `legacy/`.
- Follow each notebook's setup and input requirements; there is no single root dependency file for all experiments.
- Preserve original meeting records, experiment conditions, and existing result files.
- Do not invent results or treat plans, oracle upper bounds, and implemented methods as equivalent.
- Never publish secrets, private chat exports, or withheld paper artifacts.
- Use [CONTRIBUTING.md](CONTRIBUTING.md) for the Git workflow. Do not push directly to `main`.

## Validation

```bash
python3 .github/scripts/check_repository.py
```

This checks maintained documentation links, Python syntax, and tracked notebook/JSON structure without executing experiments or calling model APIs. GPU experiments require their own inputs and environment.

The original RAG-focused assistant guide is retained as a [historical document](docs/archive/start-agent-guide.md).
